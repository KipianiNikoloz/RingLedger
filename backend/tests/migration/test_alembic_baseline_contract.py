from __future__ import annotations

import importlib.util
import subprocess
import sys
import unittest
from pathlib import Path


class AlembicBaselineContractTests(unittest.TestCase):
    def test_baseline_revision_uses_deterministic_naming_and_downgrade(self) -> None:
        versions_dir = Path(__file__).resolve().parents[2] / "alembic" / "versions"
        revision_files = sorted(path for path in versions_dir.glob("*.py") if path.name != "__init__.py")
        self.assertGreaterEqual(len(revision_files), 1)

        baseline = revision_files[0]
        self.assertRegex(baseline.stem, r"^\d{12}_[a-z0-9_]+$")

        spec = importlib.util.spec_from_file_location("alembic_baseline", baseline)
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader)

        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        self.assertEqual(module.revision, baseline.stem)
        self.assertIsNone(module.down_revision)
        self.assertTrue(callable(module.upgrade))
        self.assertTrue(callable(module.downgrade))

    def test_alembic_ini_defines_script_location(self) -> None:
        ini_path = Path(__file__).resolve().parents[2] / "alembic.ini"
        text = ini_path.read_text(encoding="utf-8")

        self.assertIn("[alembic]", text)
        self.assertIn("script_location = %(here)s/alembic", text)
        self.assertIn("sqlalchemy.url", text)

    def test_alembic_offline_upgrade_and_downgrade_sql_compile(self) -> None:
        repo_root = Path(__file__).resolve().parents[3]
        upgrade = subprocess.run(
            [sys.executable, "-m", "alembic", "-c", "backend/alembic.ini", "upgrade", "head", "--sql"],
            cwd=repo_root,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(upgrade.returncode, 0, msg=upgrade.stderr)
        self.assertIn("CREATE TABLE users", upgrade.stdout)

        downgrade = subprocess.run(
            [sys.executable, "-m", "alembic", "-c", "backend/alembic.ini", "downgrade", "head:base", "--sql"],
            cwd=repo_root,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(downgrade.returncode, 0, msg=downgrade.stderr)
        self.assertIn("DROP TABLE users", downgrade.stdout)


if __name__ == "__main__":
    unittest.main()
