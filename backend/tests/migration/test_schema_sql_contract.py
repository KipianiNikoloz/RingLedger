from __future__ import annotations

from pathlib import Path
import unittest


class SchemaSqlContractTests(unittest.TestCase):
    def test_schema_contains_required_enums_and_bigint_fields(self) -> None:
        sql_path = Path(__file__).resolve().parents[2] / "sql" / "001_init_schema.sql"
        text = sql_path.read_text(encoding="utf-8")

        self.assertIn("CREATE TYPE user_role", text)
        self.assertIn("CREATE TYPE bout_status", text)
        self.assertIn("CREATE TYPE escrow_kind", text)
        self.assertIn("CREATE TYPE escrow_status", text)
        self.assertIn("CREATE TYPE bout_winner", text)

        for column in ["show_a_drops BIGINT", "show_b_drops BIGINT", "bonus_a_drops BIGINT", "bonus_b_drops BIGINT"]:
            self.assertIn(column, text)


if __name__ == "__main__":
    unittest.main()

