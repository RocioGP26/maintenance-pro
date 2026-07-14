"""Incrementa la versión canónica y sincroniza la documentación de release."""

from __future__ import annotations

import argparse
import re
from datetime import date
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VERSION_FILE = ROOT / "app" / "version.py"
CHANGELOG_FILE = ROOT / "CHANGELOG.md"
VERSIONS_FILE = ROOT / "docs" / "VERSIONS.md"

VERSION_RE = re.compile(r'^__version__ = "(\d+)\.(\d+)\.(\d+)"$', re.MULTILINE)


def bump_version(current: str, bump: str) -> str:
    major, minor, patch = (int(part) for part in current.split("."))
    if bump == "major":
        return f"{major + 1}.0.0"
    if bump == "minor":
        return f"{major}.{minor + 1}.0"
    if bump == "patch":
        return f"{major}.{minor}.{patch + 1}"
    raise ValueError(f"Incremento no válido: {bump}")


def update_version_source(text: str, new_version: str) -> tuple[str, str]:
    match = VERSION_RE.search(text)
    if not match:
        raise ValueError("No se encontró __version__ canónica")
    current = ".".join(match.groups())
    return VERSION_RE.sub(f'__version__ = "{new_version}"', text, count=1), current


def update_changelog(
    text: str,
    *,
    old_version: str,
    new_version: str,
    release_date: str,
    summary: str,
) -> str:
    pattern = re.compile(r"(?ms)^## \[Unreleased\]\s*\n(.*?)(?=^## \[)")
    match = pattern.search(text)
    if not match:
        raise ValueError("CHANGELOG.md no contiene la sección Unreleased")
    pending = match.group(1).strip()
    placeholder = "### Added\n\n- Espacio reservado para cambios aún no publicados."
    if pending == placeholder or not pending:
        release_body = f"### Changed\n\n- {summary}."
    else:
        release_body = f"{pending}\n\n### Notes\n\n- {summary}."
    replacement = (
        "## [Unreleased]\n\n"
        f"{placeholder}\n\n"
        f"## [{new_version}] - {release_date}\n\n"
        f"{release_body}\n\n"
    )
    text = pattern.sub(replacement, text, count=1)
    unreleased = (
        f"[Unreleased]: https://github.com/RocioGP26/maintenance-pro/compare/"
        f"v{new_version}...HEAD"
    )
    text = re.sub(r"(?m)^\[Unreleased\]: .*$", unreleased, text, count=1)
    release_link = (
        f"[{new_version}]: https://github.com/RocioGP26/maintenance-pro/compare/"
        f"v{old_version}...v{new_version}"
    )
    if not re.search(rf"(?m)^\[{re.escape(new_version)}\]:", text):
        text = text.rstrip() + "\n" + release_link + "\n"
    return text


def update_versions_document(text: str, new_version: str) -> str:
    pattern = re.compile(r"(?m)^(\| \*\*Aplicación Flask\*\* \| )\*\*v[^*]+\*\*( \|)")
    updated, count = pattern.subn(rf"\g<1>**v{new_version}**\g<2>", text, count=1)
    if count != 1:
        raise ValueError("No se encontró la versión de Aplicación Flask en docs/VERSIONS.md")
    return updated


def release(*, bump: str, summary: str, release_date: str | None = None) -> str:
    version_text = VERSION_FILE.read_text(encoding="utf-8")
    match = VERSION_RE.search(version_text)
    if not match:
        raise ValueError("No se encontró la versión actual")
    old_version = ".".join(match.groups())
    new_version = bump_version(old_version, bump)
    normalized_summary = " ".join(summary.strip().split()).rstrip(".") or "Release automático"
    day = release_date or date.today().isoformat()

    version_text, _ = update_version_source(version_text, new_version)
    changelog_text = update_changelog(
        CHANGELOG_FILE.read_text(encoding="utf-8"),
        old_version=old_version,
        new_version=new_version,
        release_date=day,
        summary=normalized_summary,
    )
    versions_text = update_versions_document(
        VERSIONS_FILE.read_text(encoding="utf-8"), new_version
    )

    VERSION_FILE.write_text(version_text, encoding="utf-8")
    CHANGELOG_FILE.write_text(changelog_text, encoding="utf-8")
    VERSIONS_FILE.write_text(versions_text, encoding="utf-8")
    return new_version


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bump", choices=("patch", "minor", "major"), required=True)
    parser.add_argument("--summary", default="Release automático")
    parser.add_argument("--date", dest="release_date")
    args = parser.parse_args()
    print(release(bump=args.bump, summary=args.summary, release_date=args.release_date))


if __name__ == "__main__":
    main()
