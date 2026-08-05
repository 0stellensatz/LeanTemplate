#!/usr/bin/env python3
"""Structural check for the Lake project this script sits in.

It ships in the template repository and so sits at the root of every project
generated from it, where it checks that project and nothing else.  The project
name is read off the directory this file sits in -- so a rename needs no edit
here, but a checkout directory that does not carry the package name will fail.
Run it from the project root, or wire it into a hook or a CI step:

    python3 __check__.py

One check, textual (no build, no Lean required):

    Root imports --- the root module `<Project>/<Project>.lean` must directly
    import every module of the project, and import nothing that has no source
    file.  This is checked rather than left to the build because the failure is
    silent: a file missing from the import list is not built, is not
    type-checked, and reports nothing at all.  A `lake build` of a project with a
    dropped file is as green as one without.

Exit status is 0 when the project is clean, 1 otherwise.
"""

from __future__ import annotations

import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parent
NAME = PROJECT.name


def module_name(source: Path, lib_root: Path) -> str:
    parts = list(source.relative_to(lib_root).with_suffix("").parts)
    escaped = [p if not p[0].isdigit() else f"«{p}»" for p in parts]
    return ".".join([NAME] + escaped)


def project_modules() -> dict[str, Path]:
    """Map every module of the project to its source file, root module included."""
    lib_root = PROJECT / NAME
    modules = {}
    if lib_root.is_dir():
        modules = {
            module_name(source, lib_root): source
            for source in sorted(lib_root.rglob("*.lean"))
        }
    root_module = PROJECT / f"{NAME}.lean"
    if root_module.is_file():
        modules[NAME] = root_module
    return modules


def read_imports(source: Path) -> list[str]:
    """The modules a file imports directly, in source order."""
    return [
        line.split(None, 1)[1].strip()
        for line in source.read_text(encoding="utf-8").splitlines()
        if line.startswith("import ")
    ]


def check_root_imports(errors: list[str], modules: dict[str, Path]) -> None:
    if not (PROJECT / NAME).is_dir():
        errors.append(f"the library directory {NAME}/ is missing")
        return
    if NAME not in modules:
        errors.append(f"the root module {NAME}.lean is missing")
        return

    imported = set(read_imports(modules[NAME]))
    expected = {name for name in modules if name != NAME}

    for missing in sorted(expected - imported):
        errors.append(f"{NAME}.lean: does not import {missing}")
    for extra in sorted(
        name for name in imported - expected if name.startswith(f"{NAME}.")
    ):
        errors.append(f"{NAME}.lean: imports {extra}, which has no source file")


def main() -> int:
    if not (PROJECT / "lakefile.toml").is_file():
        print(f"error: {PROJECT} is not a Lake project (no lakefile.toml)", file=sys.stderr)
        return 1

    errors: list[str] = []
    check_root_imports(errors, project_modules())

    for error in errors:
        print(f"error: {error}")
    if errors:
        print(f"\n{len(errors)} error(s) in {NAME}")
        return 1
    print(f"ok: {NAME}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
