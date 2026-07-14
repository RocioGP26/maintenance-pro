"""Pruebas del versionador automático sin modificar archivos reales."""

import unittest

from scripts.release_version import (
    bump_version,
    update_changelog,
    update_version_source,
    update_versions_document,
)


class TestAutomatedReleaseVersion(unittest.TestCase):
    def test_semver_bumps(self):
        self.assertEqual(bump_version("1.2.3", "patch"), "1.2.4")
        self.assertEqual(bump_version("1.2.3", "minor"), "1.3.0")
        self.assertEqual(bump_version("1.2.3", "major"), "2.0.0")

    def test_updates_canonical_source(self):
        updated, old = update_version_source('__version__ = "1.0.0"\n', "1.1.0")
        self.assertEqual(old, "1.0.0")
        self.assertIn('__version__ = "1.1.0"', updated)

    def test_changelog_preserves_pending_notes_and_links_release(self):
        source = """# Changelog

## [Unreleased]

### Added

- Nueva función.

## [1.0.0] - 2026-01-01

- Inicial.

[Unreleased]: https://github.com/RocioGP26/maintenance-pro/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/RocioGP26/maintenance-pro/releases/tag/v1.0.0
"""
        updated = update_changelog(
            source,
            old_version="1.0.0",
            new_version="1.1.0",
            release_date="2026-07-14",
            summary="Nueva capacidad",
        )
        self.assertIn("## [1.1.0] - 2026-07-14", updated)
        self.assertIn("- Nueva función.", updated)
        self.assertIn("v1.1.0...HEAD", updated)
        self.assertIn("v1.0.0...v1.1.0", updated)

    def test_updates_versions_table(self):
        source = "| **Aplicación Flask** | **v1.0.0** | fuente |\n"
        self.assertIn("**v1.0.1**", update_versions_document(source, "1.0.1"))


if __name__ == "__main__":
    unittest.main()
