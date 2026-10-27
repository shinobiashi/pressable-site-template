#!/usr/bin/env bash
#
# Check that every theme and plugin in this repository is deployed by
# .deployignore, that nothing outside the repository is reopened, and that no
# development file is tracked inside a theme or plugin folder.
#
# Pressable deploys the theme and the plugin as whole folders: CLAUDE.md, src/
# and package-lock.json inside them reached production although .deployignore
# excluded them (seen on 2026-10-27). So development files must not be inside
# those folders at all; the block build environment lives in blocks/ and the
# guides in .claude/rules/. This script fails when:
#   - a theme / plugin tracked by Git has no "!<dir>/" line below
#     "wp-content/themes/*" (or ".../plugins/*"), so it would not be deployed,
#   - a "!wp-content/..." line reopens something that is not in the repository
#     (the copy on the server would be deleted by Sync-As-Is), or
#   - a development file (CLAUDE.md, README.md, src/, package.json, ...) is
#     tracked anywhere inside a theme or plugin folder. Third-party code under a
#     vendor/ folder is not checked.
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
# expression for a whole name). "[.]" is used instead of "\." because awk would
# treat "\." in a -v value as an escape sequence.
dev_re='CLAUDE[.]md|README[.]md|src|node_modules|package[.]json|package-lock[.]json|[.]nvmrc|[.]editorconfig|[.]eslintrc.*|[.]prettierrc.*|[.]DS_Store|tests|phpunit[.]xml([.]dist)?|composer[.](json|lock)'

# Line number of the last exact match of $1, or 0.
line_no() {
	grep -nxF -- "$1" "$file" | tail -n 1 | cut -d: -f1 | grep . || echo 0
}

error() {
	echo "::error file=$file::$1"
	status=1
}

status=0
scanned=0

# Themes and plugins in the repository, found from the tracked files (not from
# .deployignore, so a missing "!" line for a whole theme or plugin is caught).
dirs=$(git ls-files -- wp-content/themes wp-content/plugins | cut -d/ -f1-3 | grep -E '^wp-content/(themes|plugins)/[^/]+$' | sort -u || true)
if [ -z "$dirs" ]; then
	error "No theme or plugin is tracked under wp-content/themes or wp-content/plugins."
	exit 1
fi

# Every "!wp-content/..." line must point to something in the repository.
reopened=$(grep -E '^!wp-content/[^*]+$' "$file" | sed -e 's/^!//' -e 's#/$##' || true)
for path in $reopened; do
	if [ -z "$(git ls-files -- "$path" | head -n 1)" ]; then
		error "\"!$path\" reopens something that is not in the repository. The copy on the server would be deleted by Sync-As-Is. Remove the line."
	fi
done

for dir in $dirs; do
	parent=${dir%/*}
	if ! [ "$(line_no "!$dir/")" -gt "$(line_no "$parent/*")" ]; then
		error "$dir/ is not deployed. Add the line \"!$dir/\" below \"$parent/*\"."
	fi

	# Development files anywhere inside the theme / plugin are deployed with it.
	tracked=$(git ls-files -- "$dir")
	scanned=$((scanned + $(printf '%s\n' "$tracked" | grep -c . || true)))
	# Fields 1-3 are wp-content/<type>/<slug>; look at the names below them, and
	# skip third-party code under vendor/.
	found=$(printf '%s\n' "$tracked" | LC_ALL=C awk -F/ -v re="^($dev_re)\$" '
		{
			for (i = 4; i <= NF; i++) {
				if ($i == "vendor") next
				if ($i ~ re) { print; next }
			}
		}')
	while IFS= read -r path; do
		if [ -n "$path" ]; then
			error "$path is a development file inside $dir/, which is deployed as a whole folder. Move it out of $dir/ (block sources go to blocks/, guides to .claude/rules/)."
		fi
	done <<-EOF
		$found
	EOF
done

if [ "$status" -eq 0 ]; then
	echo "OK: .deployignore deploys $(printf '%s\n' "$dirs" | wc -l | tr -d ' ') theme(s)/plugin(s), and no development file is inside them ($scanned files checked)."
fi
exit "$status"
