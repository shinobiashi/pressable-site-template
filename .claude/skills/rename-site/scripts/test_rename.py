#!/usr/bin/env python3
"""Scenario tests for rename.py.

Each test copies this repository's files (tracked and not ignored) into a temporary Git
repository, runs that copy's rename.py, and checks the result. Nothing in this repository
is modified.

    python3 -I .claude/skills/rename-site/scripts/test_rename.py
"""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
SKILL = Path(".claude/skills/rename-site")
SCRIPT = SKILL / "scripts" / "rename.py"
# The skill itself and the review records (which quote names freely) are not checked for names.
UNCHECKED_PREFIXES = (".claude/skills/rename-site/", "docs/")


def git(cwd: Path, *args: str) -> str:
    result = subprocess.run(["git", "-C", str(cwd), *args], check=True, capture_output=True, text=True)
    return result.stdout


class RenameScenarios(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = Path(tempfile.mkdtemp(prefix="rename-site-test-"))
        self.repo = self.tmp / "site"
        names = git(REPO, "ls-files", "-z", "--cached", "--others", "--exclude-standard").split("\0")
        for name in filter(None, names):
            src = REPO / name
            if not src.is_file():
                continue
            dest = self.repo / name
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dest)
        git(self.repo, "init", "-q", "-b", "main")
        self.commit("template")

    def tearDown(self) -> None:
        shutil.rmtree(self.tmp, ignore_errors=True)

    def commit(self, message: str) -> None:
        git(self.repo, "add", "-A")
        git(self.repo, "-c", "user.name=test", "-c", "user.email=test@example.invalid", "commit", "-q", "-m", message)

    def rename(self, theme_slug: str, plugin_slug: str, *, site: str = "サンプル商店", theme_name: str = "Sample Store",
               plugin_name: str = "Sample Store Functions", script: Path | None = None,
               extra: tuple[str, ...] = ()) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, "-I", str(script or self.repo / SCRIPT), "--site-name", site, "--theme-name", theme_name,
             "--theme-slug", theme_slug, "--plugin-name", plugin_name, "--plugin-slug", plugin_slug, *extra],
            capture_output=True, text=True,
        )

    def remove_skill(self, *extra: str) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, "-I", str(self.repo / SCRIPT), "--remove-skill", *extra], capture_output=True, text=True,
        )

    def set_template_origin(self) -> None:
        git(self.repo, "remote", "add", "origin", "git@github.com:example/pressable-site-template.git")

    def assert_unchanged(self, result: subprocess.CompletedProcess) -> None:
        self.assertEqual(result.returncode, 1, msg=result.stdout + result.stderr)
        self.assertEqual(git(self.repo, "status", "--porcelain"), "")

    def read(self, rel: str) -> str:
        return (self.repo / rel).read_text(encoding="utf-8")

    def repo_text(self) -> str:
        """All tracked text outside the skill itself and the review records."""
        texts = []
        for name in git(self.repo, "ls-files", "-z").split("\0"):
            if name and not name.startswith(UNCHECKED_PREFIXES) and (self.repo / name).is_file():
                texts.append((self.repo / name).read_text(encoding="utf-8", errors="ignore"))
        return "\n".join(texts)

    def assert_ok(self, result: subprocess.CompletedProcess) -> None:
        self.assertEqual(result.returncode, 0, msg=result.stdout + result.stderr)

    def test_full_rename(self) -> None:
        self.assert_ok(self.rename("sample-store", "sample-store-functions"))

        self.assertTrue((self.repo / "wp-content/themes/sample-store/style.css").is_file())
        self.assertTrue((self.repo / "wp-content/plugins/sample-store-functions/sample-store-functions.php").is_file())
        text = self.repo_text()
        for old in ("pressable-theme", "pressable_theme", "PRESSABLE_THEME", "pressable-plugin", "pressable_plugin", "PRESSABLE_PLUGIN"):
            self.assertNotIn(old, text)
        self.assertIn("Theme Name: Sample Store\n", self.read("wp-content/themes/sample-store/style.css"))
        self.assertIn("!/wp-content/plugins/sample-store-functions/", self.read(".gitignore"))
        self.assertIn("!wp-content/plugins/sample-store-functions/", self.read(".deployignore"))
        self.assertIn("wp:sample-store-functions/copyright", self.read("wp-content/themes/sample-store/parts/footer.html"))
        self.assertTrue(self.read("README.md").startswith("# サンプル商店\n"))

    def test_partial_rename_keeps_unchanged_slug_that_contains_the_renamed_one(self) -> None:
        # The recommended pairing: the plugin slug starts with the theme slug.
        self.assert_ok(self.rename("sample-store", "sample-store-functions"))
        self.commit("rename")

        self.assert_ok(self.rename("acme-theme", "sample-store-functions", theme_name="Acme Theme"))

        self.assertTrue((self.repo / "wp-content/themes/acme-theme/style.css").is_file())
        self.assertTrue((self.repo / "wp-content/plugins/sample-store-functions/sample-store-functions.php").is_file())
        self.assertNotIn("acme-theme-functions", self.repo_text())
        self.assertNotIn("ACME_THEME_FUNCTIONS", self.repo_text())
        self.assertIn("!wp-content/plugins/sample-store-functions/", self.read(".deployignore"))
        self.assertIn("Text Domain:       sample-store-functions", self.read("wp-content/plugins/sample-store-functions/sample-store-functions.php"))
        self.assertIn("Text Domain: acme-theme\n", self.read("wp-content/themes/acme-theme/style.css"))

    def test_new_slug_that_contains_the_old_slug(self) -> None:
        self.assert_ok(self.rename("pressable-theme-jp", "pressable-plugin-jp"))

        text = self.repo_text()
        self.assertNotIn("pressable-theme-jp-jp", text)
        self.assertIn("Text Domain: pressable-theme-jp\n", self.read("wp-content/themes/pressable-theme-jp/style.css"))

    def test_generic_slug_does_not_touch_other_identifiers(self) -> None:
        self.assert_ok(self.rename("shop", "shop-tools"))
        self.commit("rename to a generic slug")

        self.assert_ok(self.rename("acme-theme", "acme-tools"))

        functions = self.read("wp-content/themes/acme-theme/functions.php")
        self.assertIn("'loop_shop_per_page'", functions)
        self.assertIn("acme_theme_products_per_page", functions)
        self.assertIn(".acme-theme-shop-layout", self.read("wp-content/themes/acme-theme/assets/css/theme.css"))
        # PHPCS keeps the text domain in the slug form and the prefix in the snake form.
        phpcs = self.read(".phpcs.xml.dist")
        self.assertIn('<element value="acme-theme"/>', phpcs)
        self.assertIn('<element value="acme_theme"/>', phpcs)
        self.assertIn('<element value="acme_tools"/>', phpcs)

    def test_invalid_input_changes_nothing(self) -> None:
        for args in (("same-slug", "same-slug"), ("Bad_Slug", "sample-store-functions"), ("wp-store", "sample-store-functions")):
            with self.subTest(args=args):
                result = self.rename(*args)
                self.assertEqual(result.returncode, 1, msg=result.stdout + result.stderr)
                self.assertEqual(git(self.repo, "status", "--porcelain"), "")

    def test_outside_a_git_work_tree_changes_nothing(self) -> None:
        # Without a Git file list the script must not fall back to scanning the whole folder,
        # which in a Studio site also holds WordPress core, uploads and other plugins.
        shutil.rmtree(self.repo / ".git")
        # Look up the current names, so the test also passes after the site has been renamed.
        style = next((self.repo / "wp-content/themes").glob("*/style.css"))
        plugin_dir = next((self.repo / "wp-content/plugins").iterdir())
        before = style.read_text(encoding="utf-8")

        result = self.rename("sample-store", "sample-store-functions")

        self.assertEqual(result.returncode, 1, msg=result.stdout + result.stderr)
        self.assertIn("Git の作業ツリーではありません", result.stderr)
        self.assertEqual(style.read_text(encoding="utf-8"), before)
        self.assertTrue((plugin_dir / f"{plugin_dir.name}.php").is_file())

    def test_same_values_is_a_no_op(self) -> None:
        self.assert_ok(self.rename("sample-store", "sample-store-functions"))
        self.commit("rename")

        result = self.rename("sample-store", "sample-store-functions")

        self.assert_ok(result)
        self.assertIn("変更はありません", result.stdout)
        self.assertEqual(git(self.repo, "status", "--porcelain"), "")

    def test_template_itself_is_never_renamed(self) -> None:
        self.set_template_origin()

        result = self.rename("sample-store", "sample-store-functions")

        self.assert_unchanged(result)
        self.assertIn("テンプレート", result.stderr)

    def test_remove_skill_after_rename(self) -> None:
        result = self.rename("sample-store", "sample-store-functions")
        self.assert_ok(result)
        self.assertIn("--remove-skill", result.stdout)
        self.commit("rename")

        self.assert_ok(self.remove_skill("--dry-run"))
        self.assertEqual(git(self.repo, "status", "--porcelain"), "")
        self.assert_ok(self.remove_skill())

        self.assertFalse((self.repo / SKILL).exists())
        self.assertEqual(git(self.repo, "ls-files", str(SKILL)), "")
        text = self.repo_text()
        self.assertNotIn("rename-site:start", text)
        self.assertNotIn("rename-site:end", text)
        self.assertNotIn("rename-site/", self.read(".gitignore"))
        workflow = self.read(".github/workflows/lint.yml")
        self.assertNotIn("rename-skill", workflow)
        self.assertIn("\n  phpcs:\n", workflow)
        self.assertIn("\n      - run: composer lint\n\n  blocks:\n", workflow)
        self.assertNotIn("test_rename.py", self.read("CLAUDE.md") + self.read("README.md"))
        self.assertNotIn("## サイト名・テーマ・プラグインの名前を変更する", self.read("README.md"))
        self.assertIn("（スキルは最後に、このリポジトリから自分自身を削除します）", self.read("README.md"))
        for name in (".gitignore", ".github/workflows/lint.yml", "README.md", "CLAUDE.md"):
            self.assertNotIn("\n\n\n", self.read(name), msg=name)

    def test_rename_after_removing_the_skill_with_the_templates_script(self) -> None:
        self.assert_ok(self.rename("sample-store", "sample-store-functions"))
        self.assert_ok(self.remove_skill())
        self.commit("rename and remove the skill")

        result = self.rename("acme-store", "acme-store-functions", theme_name="Acme Store",
                             script=REPO / SCRIPT, extra=("--repo", str(self.repo)))

        self.assert_ok(result)
        self.assertIn("Text Domain: acme-store\n", self.read("wp-content/themes/acme-store/style.css"))
        self.assertTrue((self.repo / "wp-content/plugins/acme-store-functions/acme-store-functions.php").is_file())
        self.assertNotIn("--remove-skill", result.stdout)

    def test_remove_skill_refuses_in_the_template(self) -> None:
        self.set_template_origin()

        self.assert_unchanged(self.remove_skill())
        self.assertTrue((self.repo / SKILL / "SKILL.md").is_file())

    def test_remove_skill_refuses_before_rename(self) -> None:
        if not self.read("README.md").startswith("# pressable-site-template\n"):
            self.skipTest("this repository has already been renamed")

        self.assert_unchanged(self.remove_skill())

    def test_remove_skill_with_a_stray_marker_changes_nothing(self) -> None:
        self.assert_ok(self.rename("sample-store", "sample-store-functions"))
        readme = self.repo / "README.md"
        heading, rest = readme.read_text(encoding="utf-8").split("\n", 1)
        # Before the first real block: must not widen that block's removal.
        readme.write_text(f"{heading}\n\n<!-- rename-site:start -->\n{rest}", encoding="utf-8")
        self.commit("rename, with a stray marker")

        result = self.remove_skill()

        self.assert_unchanged(result)
        self.assertIn("対応が取れていません", result.stderr)


if __name__ == "__main__":
    unittest.main()
