#!/usr/bin/env bash
#
# Check that .deployignore deploys every runtime file of the themes and plugins
# in this repository, none of their development files, and nothing that is not
# in the repository.
#
# On Pressable, CLAUDE.md, src/ and package-lock.json inside the theme and the
# plugin were deployed although later lines excluded them (seen on 2026-10-27).
# So .deployignore closes each theme / plugin directory again with "<dir>/*"
# right after "!<dir>/" and reopens only its runtime files with "!" lines, the
# same shape as "wp-content/*" after "!wp-content/". This script fails when:
#   - a theme / plugin tracked by Git has no "!<dir>/" line below
#     "wp-content/themes/*" (or ".../plugins/*"), so it would not be deployed,
#   - a "!wp-content/themes/<slug>/" line reopens a theme / plugin that is not
#     in the repository (the server's copy would be deleted by Sync-As-Is),
#   - a theme / plugin is reopened as a whole (no "<dir>/*" line after it),
#   - a file or folder directly under it is tracked by Git but has no "!" line
#     (it would not be deployed),
#   - a "!" line reopens a file or folder that is not in the repository (a file
#     with that name on the server would be deleted by Sync-As-Is),
#   - a development file (CLAUDE.md, src/, package.json, ...) has a "!" line, or
#   - a development file is tracked inside a reopened folder (for example
#     assets/CLAUDE.md), so it would be deployed with the folder. Third-party
#     code under a vendor/ folder is not checked.
#
# Usage: bash bin/check-deployignore.sh [path/to/.deployignore]
#        (from anywhere inside the repository; the default is the repository's)

set -eu

root=$(git rev-parse --show-toplevel)
if [ -n "${1:-}" ]; then
	file=$(cd "$(dirname "$1")" && pwd)/$(basename "$1")
else
	file=.deployignore
fi
cd "$root"

# Names of files and folders that are only for development (an extended regular
# expression for a whole name). They must not be deployed. "[.]" is used instead
# of "\." because awk would treat "\." in a -v value as an escape sequence.
dev_re='CLAUDE[.]md|README[.]md|src|node_modules|package[.]json|package-lock[.]json|[.]nvmrc|[.]editorconfig|[.]eslintrc.*|[.]prettierrc.*|[.]DS_Store|tests|phpunit[.]xml([.]dist)?|composer[.](json|lock)'

is_dev_entry() {
	printf '%s\n' "$1" | grep -Eqx -- "$dev_re"
}

# Line number of the last exact match of $1, or 0.
line_no() {
	grep -nxF -- "$1" "$file" | tail -n 1 | cut -d: -f1 | grep . || echo 0
}

# True when $1 is a line of the file below line $2 (gitignore-style rules: the last match wins).
has_line_after() {
	[ "$(line_no "$1")" -gt "$2" ]
}

error() {
	echo "::error file=$file::$1"
	status=1
}

status=0
checked=0
scanned=0

# Themes and plugins in the repository, found from the tracked files (not from
# .deployignore, so a missing "!" line for a whole theme or plugin is caught).
dirs=$(git ls-files -- wp-content/themes wp-content/plugins | cut -d/ -f1-3 | grep -E '^wp-content/(themes|plugins)/[^/]+$' | sort -u || true)
if [ -z "$dirs" ]; then
	error "No theme or plugin is tracked under wp-content/themes or wp-content/plugins."
	exit 1
fi

# "!" lines that reopen a whole theme or plugin must point to one in the repository.
reopened=$(grep -E '^!wp-content/(themes|plugins)/[^/*]+/$' "$file" | sed -e 's/^!//' -e 's#/$##' || true)
for dir in $reopened; do
	if ! printf '%s\n' "$dirs" | grep -qxF -- "$dir"; then
		error "\"!$dir/\" reopens $dir/, which is not in the repository. The copy on the server would be deleted by Sync-As-Is. Remove the line."
	fi
done

for dir in $dirs; do
	parent=${dir%/*}
	tracked=$(git ls-files -- "$dir")

	reopen=$(line_no "!$dir/")
	if ! [ "$reopen" -gt "$(line_no "$parent/*")" ]; then
		error "$dir/ is not deployed. Add the line \"!$dir/\" below \"$parent/*\"."
		continue
	fi

	close=$(line_no "$dir/*")
	if ! [ "$close" -gt "$reopen" ]; then
		error "$dir/ is deployed as a whole, so its development files are deployed too. Add \"$dir/*\" after \"!$dir/\" and a \"!\" line for each runtime file or folder."
		continue
	fi

	entries=$(printf '%s\n' "$tracked" | sed "s#^$dir/##" | cut -d/ -f1 | sort -u)
	for entry in $entries; do
		checked=$((checked + 1))
		case "$tracked" in
			*"$dir/$entry/"*) line="!$dir/$entry/" ;;
			*) line="!$dir/$entry" ;;
		esac

		if is_dev_entry "$entry"; then
			if has_line_after "$line" "$close"; then
				error "$dir/$entry is a development file but \"$line\" deploys it. Remove the line."
			fi
		elif ! has_line_after "$line" "$close"; then
			error "$dir/$entry is not deployed. Add the line \"$line\" below \"$dir/*\" (or add it to is_dev_entry in bin/check-deployignore.sh if it is only for development)."
		fi
	done

	# Development files inside a reopened folder are deployed with the folder.
	for entry in $entries; do
		if is_dev_entry "$entry" || ! has_line_after "!$dir/$entry/" "$close"; then
			continue
		fi
		inside=$(printf '%s\n' "$tracked" | grep -F -- "$dir/$entry/" || true)
		scanned=$((scanned + $(printf '%s\n' "$inside" | grep -c . || true)))
		# Fields 1-3 are wp-content/<type>/<slug> and field 4 is the folder; look at
		# the names below it, and skip third-party code under vendor/ (including a
		# reopened vendor/ folder itself).
		found=$(printf '%s\n' "$inside" | LC_ALL=C awk -F/ -v re="^($dev_re)\$" '
			{
				for (i = 4; i <= NF; i++) {
					if ($i == "vendor") next
					if (i > 4 && $i ~ re) { print; next }
				}
			}')
		while IFS= read -r path; do
			if [ -n "$path" ]; then
				error "$path is a development file inside $dir/$entry/, which is deployed with the folder. Move it out of the folder (or out of the repository)."
			fi
		done <<-EOF
			$found
		EOF
	done

	# "!" lines directly under the theme / plugin must point to something in the repository.
	lines=$(grep -E "^!$dir/[^/*]+/?\$" "$file" | sed -e "s#^!$dir/##" -e 's#/$##' || true)
	for entry in $lines; do
		if ! printf '%s\n' "$entries" | grep -qxF -- "$entry"; then
			error "\"!$dir/$entry\" reopens a file or folder that is not in the repository. A file with that name on the server would be deleted by Sync-As-Is. Remove the line (or add the file to the repository first)."
		fi
	done
done

if [ "$status" -eq 0 ]; then
	echo "OK: .deployignore deploys the runtime files of $(printf '%s\n' "$dirs" | wc -l | tr -d ' ') theme(s)/plugin(s) and none of their development files ($checked entries and $scanned files inside the reopened folders checked)."
fi
exit "$status"
