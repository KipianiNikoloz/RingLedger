from __future__ import annotations

import unittest
from dataclasses import replace
from unittest.mock import patch

from app.core.config import settings
from app.db import init_db as init_db_module


class InitDbUnitTests(unittest.TestCase):
    def test_init_db_runs_migrations_for_non_production_when_enabled(self) -> None:
        test_settings = replace(settings, app_env="development", db_auto_migrate_on_startup=True)

        with (
            patch.object(init_db_module, "settings", test_settings),
            patch.object(init_db_module, "run_db_migrations") as migrate_mock,
        ):
            init_db_module.init_db()

        migrate_mock.assert_called_once_with(revision="head")

    def test_init_db_skips_migrations_in_production(self) -> None:
        test_settings = replace(settings, app_env="production", db_auto_migrate_on_startup=True)

        with (
            patch.object(init_db_module, "settings", test_settings),
            patch.object(init_db_module, "run_db_migrations") as migrate_mock,
        ):
            init_db_module.init_db()

        migrate_mock.assert_not_called()

    def test_init_db_skips_migrations_when_disabled(self) -> None:
        test_settings = replace(settings, app_env="development", db_auto_migrate_on_startup=False)

        with (
            patch.object(init_db_module, "settings", test_settings),
            patch.object(init_db_module, "run_db_migrations") as migrate_mock,
        ):
            init_db_module.init_db()

        migrate_mock.assert_not_called()


if __name__ == "__main__":
    unittest.main()
