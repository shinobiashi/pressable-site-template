#!/usr/bin/env python3
"""Rename the site name, theme (name and slug) and plugin (name and slug) of this repository.

Usage (from the repository root):

    python3 -I .claude/skills/rename-site/scripts/rename.py \
        --site-name "サンプル商店" \
        --theme-name "Sample Store" --theme-slug sample-store \
        --plugin-name "Sample Store Functions" --plugin-slug sample-store-functions \
        --dry-run

Slugs (and the identifiers derived from them) are replaced in every text file of the
repository in a single pass. Display names are only rewritten on the specific lines
that carry them, so a generic name never touches unrelated text. Without --dry-run the
files are rewritten and the theme/plugin directories are renamed (`git mv` when tracked).
Nothing outside the repository is modified.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parents[1]
DEFAULT_REPO = Path(__file__).resolve().parents[4]

SLUG_RE = re.compile(r"^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$")
# Names are written into PHP/CSS comments, JSON strings and a shell variable.
FORBIDDEN_IN_NAMES = ['"', "\\", "$", "`", "*/", "\n", "\r"]
SKIP_DIR_NAMES = {".git", "node_modules", "vendor"}
# A slug only starts a token when it is not preceded by a letter, digit, "_" or "-":
# protects "loop_shop_per_page" and the class "<theme>-shop-layout" when the slug is "shop".
TOKEN_START = r"(?<![A-Za-z0-9_-])"


class RenameError(Exception):
    """Invalid input or repository state; nothing has been written."""


@dataclass
class Identity:
    site_name: str | None
    theme_name: str
    theme_slug: str
    plugin_name: str
    plugin_slug: str


@dataclass
class Plan:
    contents: dict[Path, tuple[str, str]] = field(default_factory=dict)  # path -> (old, new)
    token_counts: dict[Path, int] = field(default_factory=dict)
    line_rules: list[str] = field(default_factory=list)
    skipped_rules: list[str] = field(default_factory=list)
    renames: list[tuple[Path, Path]] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def slug_forms(slug: str) -> list[str]:
    """Slug, PHP prefix (snake_case) and constant prefix (UPPER_CASE)."""
    snake = slug.replace("-", "_")
    return [slug, snake, snake.upper()]


def read_text(path: Path) -> str | None:
    data = path.read_bytes()
    if b"\0" in data:
        return None
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        return None


def git_files(repo: Path) -> set[Path]:
    """Tracked and not-ignored files of the repository.

    The repository root doubles as the Studio site folder, so it also holds WordPress core,
    uploads and other plugins (all git-ignored). Only the repository's own files are renamed,
    so without a Git file list nothing is scanned at all (fail closed).
    """
    if not (repo / ".git").exists() or shutil.which("git") is None:
        raise RenameError(
            f"{repo} は Git の作業ツリーではありません（または git コマンドがありません）。"
            "Git が管理していないファイルを書き換えないよう、Git のリポジトリで実行してください。"
        )
    result = subprocess.run(
        ["git", "-C", str(repo), "ls-files", "-z", "--cached", "--others", "--exclude-standard"],
        capture_output=True,
    )
    if result.returncode != 0:
        raise RenameError(f"Git のファイル一覧を取得できませんでした: {result.stderr.decode('utf-8', 'replace').strip()}")
    return {repo / name for name in result.stdout.decode("utf-8").split("\0") if name}


def iter_repo_files(repo: Path):
    for path in sorted(git_files(repo)):
        rel_parts = path.relative_to(repo).parts
        if any(part in SKIP_DIR_NAMES for part in rel_parts):
            continue
        if path.is_symlink() or not path.is_file():
            continue
        if SKILL_DIR in path.resolve().parents:
            continue
        yield path


def find_headers(repo: Path, kind: str, main_file, header_re: str) -> list[tuple[str, str]]:
    """(slug, name) of the themes or plugins that belong to this repository."""
    root = repo / "wp-content" / kind
    tracked = git_files(repo)
    found = []
    for item_dir in sorted(root.iterdir()) if root.is_dir() else []:
        main = item_dir / main_file(item_dir.name)
        if item_dir.is_symlink() or not main.is_file():
            continue
        if main not in tracked:
            continue
        match = re.search(header_re, main.read_text(encoding="utf-8"), re.M)
        if match:
            found.append((item_dir.name, match.group(1)))
    return found


def find_themes(repo: Path) -> list[tuple[str, str]]:
    return find_headers(repo, "themes", lambda slug: "style.css", r"^Theme Name:\s*(.+?)\s*$")


def find_plugins(repo: Path) -> list[tuple[str, str]]:
    return find_headers(repo, "plugins", lambda slug: f"{slug}.php", r"^\s*\*\s*Plugin Name:\s*(.+?)\s*$")


def pick(found: list[tuple[str, str]], wanted: str | None, kind: str, flag: str) -> tuple[str, str]:
    if wanted:
        for slug, name in found:
            if slug == wanted:
                return slug, name
        raise RenameError(f"{kind}「{wanted}」が見つかりません（見つかった{kind}: {[s for s, _ in found]}）。")
    if len(found) == 1:
        return found[0]
    if not found:
        raise RenameError(f"wp-content 配下に{kind}が見つかりません。リポジトリのルートを --repo で指定してください。")
    raise RenameError(f"{kind}が複数あります: {[s for s, _ in found]}。変更元を {flag} で指定してください。")


def detect_current(repo: Path, args: argparse.Namespace) -> Identity:
    theme_slug, theme_name = pick(find_themes(repo), args.from_theme_slug, "テーマ", "--from-theme-slug")
    plugin_slug, plugin_name = pick(find_plugins(repo), args.from_plugin_slug, "プラグイン", "--from-plugin-slug")
    site_name = None
    readme = repo / "README.md"
    if readme.is_file():
        match = re.match(r"# (.+)", readme.read_text(encoding="utf-8"))
        if match and match.group(1).strip() != "pressable-site-template":
            site_name = match.group(1).strip()
    return Identity(site_name, theme_name, theme_slug, plugin_name, plugin_slug)


def validate(new: Identity, current: Identity, repo: Path) -> list[str]:
    warnings = []
    for label, slug in (("テーマスラッグ", new.theme_slug), ("プラグインスラッグ", new.plugin_slug)):
        if not SLUG_RE.match(slug):
            raise RenameError(f"{label}「{slug}」は使えません。英小文字で始まり、英小文字・数字・ハイフンだけにしてください。")
        if not 3 <= len(slug) <= 50:
            raise RenameError(f"{label}「{slug}」は 3〜50 文字にしてください。")
        if slug.startswith(("wp-", "wordpress")):
            raise RenameError(f"{label}「{slug}」は wp- / wordpress で始められません（WordPress の予約接頭辞）。")
        if "-" not in slug:
            warnings.append(
                f"{label}「{slug}」にハイフンがありません。PHP の接頭辞（{slug}_）が短く、他のプラグインと衝突しやすくなります。"
            )
    if new.theme_slug == new.plugin_slug:
        raise RenameError("テーマスラッグとプラグインスラッグは別の名前にしてください。")
    for label, name in (
        ("サイト名", new.site_name),
        ("テーマ名", new.theme_name),
        ("プラグイン名", new.plugin_name),
    ):
        if not name or not name.strip():
            raise RenameError(f"{label}が空です。")
        bad = [c for c in FORBIDDEN_IN_NAMES if c in name]
        if bad:
            raise RenameError(f"{label}「{name}」に使えない文字が含まれています: {bad}")
    if new.theme_slug != current.theme_slug and (repo / "wp-content" / "themes" / new.theme_slug).exists():
        raise RenameError(f"wp-content/themes/{new.theme_slug} が既にあります。")
    if new.plugin_slug != current.plugin_slug and (repo / "wp-content" / "plugins" / new.plugin_slug).exists():
        raise RenameError(f"wp-content/plugins/{new.plugin_slug} が既にあります。")
    return warnings


def line_rules(repo: Path, current: Identity, new: Identity):
    """(file, description, pattern, replacement) for names written on specific lines."""
    theme = repo / "wp-content" / "themes" / current.theme_slug
    plugin = repo / "wp-content" / "plugins" / current.plugin_slug
    site = new.site_name

    def snake_prefixes(match: re.Match) -> str:
        # The PHPCS prefixes are written without a trailing "_", so a hyphen-less old slug
        # ("shop") is replaced with the slug form; prefixes must be the snake form.
        body = match.group(2)
        for slug in (new.theme_slug, new.plugin_slug):
            dash, snake, _ = slug_forms(slug)
            body = body.replace(f'value="{dash}"', f'value="{snake}"')
        return match.group(1) + body + match.group(3)

    return [
        (repo / ".phpcs.xml.dist", "PHP 接頭辞（.phpcs.xml.dist の prefixes）",
         re.compile(r'(<property name="prefixes" type="array">)(.*?)(</property>)', re.S), snake_prefixes),
        (theme / "style.css", "テーマ名（style.css の Theme Name）",
         re.compile(r"^Theme Name:.*$", re.M), f"Theme Name: {new.theme_name}"),
        (theme / "style.css", "テーマの説明文のサイト名（style.css の Description）",
         re.compile(r"^Description: (?:Pressable で構築するサイト用のブロックテーマ（FSE）の雛形です。|.+?のブロックテーマ（FSE）です。)", re.M),
         f"Description: {site}のブロックテーマ（FSE）です。"),
        (theme / "functions.php", "テーマ名（functions.php の docblock）",
         re.compile(r"^ \* .+ setup\.$", re.M), f" * {new.theme_name} setup."),
        (theme / "assets" / "css" / "theme.css", "テーマ名（theme.css の先頭コメント）",
         re.compile(r"^/\* .+? — 補助スタイル", re.M), f"/* {new.theme_name} — 補助スタイル"),
        (theme / "CLAUDE.md", "テーマ名（テーマの CLAUDE.md の見出し）",
         re.compile(r"^# CLAUDE\.md — .+ 開発ガイド$", re.M), f"# CLAUDE.md — {new.theme_name} 開発ガイド"),
        (plugin / f"{current.plugin_slug}.php", "プラグイン名（Plugin Name）",
         re.compile(r"^( \* Plugin Name:\s*).*$", re.M), rf"\g<1>{new.plugin_name}"),
        (plugin / f"{current.plugin_slug}.php", "プラグインの説明文のサイト名（Description）",
         re.compile(r"^( \* Description:\s*)(?:サイト固有の機能|.+?の機能)（独自ブロック", re.M),
         rf"\g<1>{site}の機能（独自ブロック"),
        (plugin / "package.json", "プラグイン名（package.json の description）",
         re.compile(r'^(\s*"description": ").+ の独自ブロックのビルド環境(",?)$', re.M),
         rf"\g<1>{new.plugin_name} の独自ブロックのビルド環境\g<2>"),
        (plugin / "CLAUDE.md", "プラグイン名（プラグインの CLAUDE.md の見出し）",
         re.compile(r"^# CLAUDE\.md — .+ 開発ガイド$", re.M), f"# CLAUDE.md — {new.plugin_name} 開発ガイド"),
        (repo / "README.md", "サイト名（README.md の見出し）",
         re.compile(r"\A# .+$", re.M), f"# {site}"),
        (repo / "README.md", "サイト名（README.md の冒頭の説明）",
         re.compile(r"^(?:Pressable でホスティングする WordPress サイトを構築するためのテンプレートです。|.+?の WordPress サイトのリポジトリです（Pressable でホスティング）。)$", re.M),
         f"{site}の WordPress サイトのリポジトリです（Pressable でホスティング）。"),
    ]


def token_pattern(tokens) -> re.Pattern:
    """Longest first, and only where a slug can start (never right after a letter, digit, "_" or "-")."""
    alternation = "|".join(re.escape(t) for t in sorted(set(tokens), key=len, reverse=True))
    return re.compile(rf"{TOKEN_START}(?:{alternation})")


def token_rules(current: Identity, new: Identity) -> dict:
    """Old token -> replacement function, for both slugs.

    Unchanged slugs are included and map to themselves, so a renamed slug never matches
    inside them (renaming theme "sample-store" must not touch plugin "sample-store-functions").
    """
    rules = {}
    for old_slug, new_slug in ((current.theme_slug, new.theme_slug), (current.plugin_slug, new.plugin_slug)):
        old_dash, old_snake, old_upper = slug_forms(old_slug)
        new_dash, new_snake, new_upper = slug_forms(new_slug)
        if old_dash == old_snake:
            # Without a hyphen, "shop" is both the slug and the PHP prefix; "shop_" is the prefix.
            rules[old_dash] = lambda m, d=new_dash, s=new_snake: s if m.string[m.end():m.end() + 1] == "_" else d
        else:
            rules[old_dash] = lambda m, d=new_dash: d
            rules[old_snake] = lambda m, s=new_snake: s
        rules[old_upper] = lambda m, u=new_upper: u
    return rules


def build_plan(repo: Path, current: Identity, new: Identity) -> Plan:
    plan = Plan()

    rules = token_rules(current, new)
    # Single pass, so a replacement is never replaced again.
    token_re = token_pattern(rules)

    texts: dict[Path, str] = {}
    for path in iter_repo_files(repo):
        text = read_text(path)
        if text is None:
            continue
        texts[path] = text
        changed = 0

        def replace(match: re.Match) -> str:
            nonlocal changed
            replacement = rules[match.group(0)](match)
            changed += replacement != match.group(0)
            return replacement

        new_text = token_re.sub(replace, text)
        if changed:
            plan.contents[path] = (text, new_text)
            plan.token_counts[path] = changed

    for path, label, pattern, replacement in line_rules(repo, current, new):
        if path not in texts:
            plan.skipped_rules.append(f"{label}: {path.relative_to(repo)} がありません")
            continue
        base = plan.contents.get(path, (texts[path], texts[path]))[1]
        new_text, count = pattern.subn(replacement, base, count=1)
        if not count:
            plan.skipped_rules.append(f"{label}: 該当する行が見つからないため変更しません（手で直されている可能性）")
            continue
        if new_text != base:
            plan.contents[path] = (texts[path], new_text)
            plan.line_rules.append(f"{label}: {path.relative_to(repo)}")

    plugin_dir = repo / "wp-content" / "plugins" / current.plugin_slug
    if new.plugin_slug != current.plugin_slug:
        plan.renames.append((plugin_dir / f"{current.plugin_slug}.php", plugin_dir / f"{new.plugin_slug}.php"))
        plan.renames.append((plugin_dir, plugin_dir.with_name(new.plugin_slug)))
    if new.theme_slug != current.theme_slug:
        theme_dir = repo / "wp-content" / "themes" / current.theme_slug
        plan.renames.append((theme_dir, theme_dir.with_name(new.theme_slug)))

    return plan


def is_git_tracked(repo: Path, path: Path) -> bool:
    if not (repo / ".git").exists() or shutil.which("git") is None:
        return False
    result = subprocess.run(
        ["git", "-C", str(repo), "ls-files", "--error-unmatch", str(path.relative_to(repo))],
        capture_output=True,
    )
    return result.returncode == 0


def apply_plan(repo: Path, plan: Plan) -> None:
    for path, (_, new_text) in plan.contents.items():
        path.write_text(new_text, encoding="utf-8")
    for src, dest in plan.renames:
        if is_git_tracked(repo, src):
            subprocess.run(["git", "-C", str(repo), "mv", str(src.relative_to(repo)), str(dest.relative_to(repo))], check=True)
        else:
            src.rename(dest)


def post_checks(repo: Path, current: Identity, new: Identity) -> list[str]:
    problems = []
    current_tokens = slug_forms(new.theme_slug) + slug_forms(new.plugin_slug)
    old_tokens = []
    if current.theme_slug != new.theme_slug:
        old_tokens += slug_forms(current.theme_slug)
    if current.plugin_slug != new.plugin_slug:
        old_tokens += slug_forms(current.plugin_slug)
    old_tokens = [t for t in old_tokens if t not in current_tokens]
    # Hide the current names first, so an old slug inside a new one ("pressable-theme" in
    # "pressable-theme-jp") is not reported as a leftover.
    mask_re = token_pattern(current_tokens)
    leftover_re = token_pattern(old_tokens) if old_tokens else None

    php = shutil.which("php")
    for path in iter_repo_files(repo):
        text = read_text(path)
        if text is None:
            continue
        rel = path.relative_to(repo)
        if leftover_re and leftover_re.search(mask_re.sub("\0", text)):
            problems.append(f"古い名前が残っています: {rel}")
        if path.suffix == ".json":
            try:
                json.loads(text)
            except json.JSONDecodeError as error:
                problems.append(f"JSON として読めません: {rel} ({error})")
        if path.suffix == ".php" and php:
            result = subprocess.run([php, "-l", str(path)], capture_output=True, text=True)
            if result.returncode != 0:
                problems.append(f"PHP の構文エラー: {rel}\n{result.stdout.strip()}")
    return problems


def studio_notes(repo: Path) -> list[str]:
    """The repository root is also the Studio site folder once wp-config.php exists there."""
    if not (repo / "wp-config.php").is_file():
        return []
    return [
        "このリポジトリは Studio サイトのフォルダです（ローカルのデータベースは旧スラッグのテーマ・プラグインを覚えています）。",
        "  リネーム後に bin/studio-prepare.sh を実行して、新しいスラッグのテーマ・プラグインを有効化してください。",
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description="サイト名・テーマ・プラグインの名前を一括で変更する。")
    parser.add_argument("--site-name", required=True, help="サイト名（例: サンプル商店）")
    parser.add_argument("--theme-name", required=True, help="テーマ名（例: Sample Store）")
    parser.add_argument("--theme-slug", required=True, help="テーマスラッグ（例: sample-store）")
    parser.add_argument("--plugin-name", required=True, help="プラグイン名（例: Sample Store Functions）")
    parser.add_argument("--plugin-slug", required=True, help="プラグインスラッグ（例: sample-store-functions）")
    parser.add_argument("--from-theme-slug", help="変更元のテーマスラッグ（テーマが複数あるときだけ指定）")
    parser.add_argument("--from-plugin-slug", help="変更元のプラグインスラッグ（プラグインが複数あるときだけ指定）")
    parser.add_argument("--repo", type=Path, default=DEFAULT_REPO, help="リポジトリのルート（既定: このスクリプトの位置から算出）")
    parser.add_argument("--dry-run", action="store_true", help="変更内容を表示するだけで書き込まない")
    args = parser.parse_args()

    repo = args.repo.resolve()
    new = Identity(args.site_name.strip(), args.theme_name.strip(), args.theme_slug, args.plugin_name.strip(), args.plugin_slug)

    try:
        current = detect_current(repo, args)
        warnings = validate(new, current, repo)
        plan = build_plan(repo, current, new)
    except RenameError as error:
        print(f"エラー: {error}", file=sys.stderr)
        return 1

    print(f"リポジトリ: {repo}")
    print("変更内容:")
    print(f"  サイト名        {current.site_name or '（不明）'} → {new.site_name}")
    print(f"  テーマ          {current.theme_name}（{current.theme_slug}） → {new.theme_name}（{new.theme_slug}）")
    print(f"  プラグイン      {current.plugin_name}（{current.plugin_slug}） → {new.plugin_name}（{new.plugin_slug}）")
    print(f"  PHP 接頭辞      {slug_forms(current.theme_slug)[1]}_ / {slug_forms(current.plugin_slug)[1]}_"
          f" → {slug_forms(new.theme_slug)[1]}_ / {slug_forms(new.plugin_slug)[1]}_")
    print(f"  定数接頭辞      {slug_forms(current.theme_slug)[2]}_ / {slug_forms(current.plugin_slug)[2]}_"
          f" → {slug_forms(new.theme_slug)[2]}_ / {slug_forms(new.plugin_slug)[2]}_")
    print(f"  CSS クラス接頭辞 {current.theme_slug}- → {new.theme_slug}-")
    print(f"  ブロック名前空間 {current.plugin_slug}/ → {new.plugin_slug}/")

    if not plan.contents and not plan.renames:
        print("\n変更はありません（すべて現在の名前と同じです）。")
        return 0

    print(f"\n書き換えるファイル（{len(plan.contents)} 件。数字はスラッグ・接頭辞の置換数）:")
    for path in sorted(plan.contents):
        count = plan.token_counts.get(path)
        print(f"  {count if count else '-':>4}  {path.relative_to(repo)}")
    if plan.line_rules:
        print("\n名前を書き換える行:")
        for rule in plan.line_rules:
            print(f"  {rule}")
    if plan.renames:
        print("\nリネーム:")
        for src, dest in plan.renames:
            print(f"  {src.relative_to(repo)} → {dest.relative_to(repo)}")
    for item in plan.skipped_rules:
        print(f"\n注意: {item}")
    for warning in warnings:
        print(f"\n警告: {warning}")
    for note in studio_notes(repo):
        print(note if note.startswith("  ") else f"\n{note}")

    if args.dry_run:
        print("\n--dry-run のため、何も書き込んでいません。")
        return 0

    apply_plan(repo, plan)
    problems = post_checks(repo, current, new)
    print("\n書き換えました。")
    if problems:
        print("\n確認が必要な点:")
        for problem in problems:
            print(f"  {problem}")
        return 2

    plugin_rel = Path("wp-content") / "plugins" / new.plugin_slug
    print("自動チェック: 古い名前の残り・JSON・PHP 構文（php があれば）に問題はありません。")
    print("\n次の作業:")
    print(f"  1. cd {plugin_rel} && nvm use && npm ci && npm run build && npm run lint:js   # build/ を作り直し、整形を確かめる")
    print("  2. composer lint   # リポジトリのルートで")
    print("  3. Studio サイトのフォルダなら bin/studio-prepare.sh を実行する（新しいスラッグで有効化）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
