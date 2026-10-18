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
SCRIPT = Path(".claude/skills/rename-site/scripts/rename.py")
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
               plugin_name: str = "Sample Store Functions") -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, "-I", str(self.repo / SCRIPT), "--site-name", site, "--theme-name", theme_name,
             "--theme-slug", theme_slug, "--plugin-name", plugin_name, "--plugin-slug", plugin_slug],
            capture_output=True, text=True,
        )

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

    def test_same_values_is_a_no_op(self) -> None:
        self.assert_ok(self.rename("sample-store", "sample-store-functions"))
        self.commit("rename")

        result = self.rename("sample-store", "sample-store-functions")

        self.assert_ok(result)
        self.assertIn("変更はありません", result.stdout)
        self.assertEqual(git(self.repo, "status", "--porcelain"), "")


if __name__ == "__main__":
    unittest.main()
