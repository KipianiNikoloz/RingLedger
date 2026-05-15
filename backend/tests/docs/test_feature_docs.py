from __future__ import annotations

import re
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
FEATURE_DOCS_ROOT = REPO_ROOT / "docs" / "features"

FEATURE_READMES = [
    "auth-and-role-guards/README.md",
    "fighter-profiles/README.md",
    "bout-management/README.md",
    "escrow-creation/README.md",
    "xaman-signing-reconciliation/README.md",
    "result-entry-payouts/README.md",
    "idempotency-failure-taxonomy/README.md",
    "xrpl-validation-crypto-conditions/README.md",
    "persistence-migrations-uow/README.md",
    "frontend-operator-console/README.md",
    "testnet-release-readiness/README.md",
]

REQUIRED_HEADINGS = [
    "## Purpose",
    "## Maintainer Map",
    "## Runtime Flow",
    "## Key Invariants",
    "## Diagrams",
    "## Tests",
    "## Operational Notes",
    "## Canonical References",
]

REPO_PATH_PREFIXES = (
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


class FeatureDocsTests(unittest.TestCase):
    def test_feature_docs_hub_links_all_required_readmes(self) -> None:
        hub_path = FEATURE_DOCS_ROOT / "README.md"
        self.assertTrue(hub_path.exists(), "Feature documentation hub is missing")

        hub = hub_path.read_text(encoding="utf-8")
        self.assertIn("```mermaid", hub)
        for readme in FEATURE_READMES:
            self.assertIn(f"`docs/features/{readme}`", hub)

    def test_feature_readmes_follow_maintainer_template(self) -> None:
        for readme in FEATURE_READMES:
            with self.subTest(readme=readme):
                path = FEATURE_DOCS_ROOT / readme
                self.assertTrue(path.exists(), f"Missing feature README: {readme}")
                markdown = path.read_text(encoding="utf-8")

                for heading in REQUIRED_HEADINGS:
                    self.assertIn(heading, markdown)

                self.assertIn("```mermaid", markdown)

    def test_referenced_repo_paths_exist(self) -> None:
        markdown_files = [FEATURE_DOCS_ROOT / "README.md", *(FEATURE_DOCS_ROOT / readme for readme in FEATURE_READMES)]

        missing: list[str] = []
        for markdown_file in markdown_files:
            markdown = markdown_file.read_text(encoding="utf-8")
            for repo_path in _repo_paths_from_markdown(markdown):
                if not (REPO_ROOT / repo_path).exists():
                    missing.append(f"{markdown_file.relative_to(REPO_ROOT)} -> {repo_path}")

        self.assertEqual([], missing)


if __name__ == "__main__":
    unittest.main()
