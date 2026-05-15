from __future__ import annotations

import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]

MODULE_READMES = [
    "backend/app/README.md",
    "backend/app/api/README.md",
    "backend/app/api/bouts_routes/README.md",
    "backend/app/core/README.md",
    "backend/app/crypto_conditions/README.md",
    "backend/app/db/README.md",
    "backend/app/domain/README.md",
    "backend/app/integrations/README.md",
    "backend/app/middleware/README.md",
    "backend/app/models/README.md",
    "backend/app/repositories/README.md",
    "backend/app/schemas/README.md",
    "backend/app/services/README.md",
    "backend/tests/README.md",
    "frontend/src/README.md",
    "frontend/src/api/README.md",
    "frontend/src/app/README.md",
    "frontend/src/components/README.md",
    "frontend/src/hooks/README.md",
]

REQUIRED_HEADINGS = [
    "## Purpose",
    "## Directory Map",
    "## Diagrams",
    "## Maintenance Notes",
    "## Related Docs",
]

REPO_PATH_PREFIXES = (
    ".github/",
    "README.md",
    "backend/",
    "docs/",
    "frontend/",
    "openspec/",
    "pyproject.toml",
)


def _repo_paths_from_markdown(markdown: str) -> set[str]:
    paths: set[str] = set()
    for match in re.finditer(r"`([^`]+)`", markdown):
        value = match.group(1)
        if value == "README.md" or value.startswith(REPO_PATH_PREFIXES):
            paths.add(value)
    return paths


class ModuleReadmeTests(unittest.TestCase):
    def test_required_module_readmes_exist_and_follow_template(self) -> None:
        for readme in MODULE_READMES:
            with self.subTest(readme=readme):
                path = REPO_ROOT / readme
                self.assertTrue(path.exists(), f"Missing module README: {readme}")
                markdown = path.read_text(encoding="utf-8")

                for heading in REQUIRED_HEADINGS:
                    self.assertIn(heading, markdown)

                self.assertIn("```mermaid", markdown)

    def test_root_readme_links_module_documentation(self) -> None:
        root_readme = (REPO_ROOT / "README.md").read_text(encoding="utf-8")

        self.assertIn("```mermaid", root_readme)
        for readme in MODULE_READMES:
            self.assertIn(f"`{readme}`", root_readme)

    def test_referenced_repo_paths_exist(self) -> None:
        markdown_files = [REPO_ROOT / "README.md", *(REPO_ROOT / readme for readme in MODULE_READMES)]

        missing: list[str] = []
        for markdown_file in markdown_files:
            markdown = markdown_file.read_text(encoding="utf-8")
            for repo_path in _repo_paths_from_markdown(markdown):
                if not (REPO_ROOT / repo_path).exists():
                    missing.append(f"{markdown_file.relative_to(REPO_ROOT)} -> {repo_path}")

        self.assertEqual([], missing)


if __name__ == "__main__":
    unittest.main()
