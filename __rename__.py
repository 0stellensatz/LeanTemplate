#!/usr/bin/env python3
"""Rename this template checkout to the project it is becoming.

A GitHub template repository copies files verbatim---it substitutes nothing---so
a repository generated from `LeanTemplate` still calls its Lake package, its
library directory, and its root all-import module `LeanTemplate`.  Run this once,
from the repository root, before writing any Lean:

    python3 __rename__.py <Project>

It renames the two paths that carry the name, rewrites every textual occurrence
of `LeanTemplate` in the tracked files, cuts the template half of `README.md` at
its `TEMPLATE-README-ENDS-HERE` sentinel, and then deletes itself---a template's
rename step is not part of the project it produced.  Nothing else is touched: the
`__docs__/` rule copies, `__check__.py`, and the Lake files stay as they are, and
pruning the rules that do not apply is a separate, deliberate step (see
`README.md`).

`__check__.py` needs no rewriting: it derives the project name from the directory
it sits in, so it follows the rename automatically.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OLD = "LeanTemplate"

# Everything under these is either git's own storage or a machine-local build
# artifact; neither is ours to rewrite.
SKIP_DIRS = {".git", ".lake"}

# A Lean module name component, which a directory name must also be.
NAME_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_]*$")

# Marks the end of the template's own half of the README; the project keeps only
# what follows it.
README_SENTINEL = "TEMPLATE-README-ENDS-HERE"


def fail(message: str) -> None:
    print(f"error: {message}", file=sys.stderr)
    raise SystemExit(1)


def in_git_worktree() -> bool:
    result = subprocess.run(
        ["git", "-C", str(ROOT), "rev-parse", "--is-inside-work-tree"],
        capture_output=True,
        text=True,
    )
    return result.returncode == 0 and result.stdout.strip() == "true"


def move(source: Path, target: Path, use_git: bool) -> None:
    """Rename `source` to `target`, staging it with git when that is available."""
    if use_git:
        result = subprocess.run(
            ["git", "-C", str(ROOT), "mv", str(source.relative_to(ROOT)), str(target.relative_to(ROOT))],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            return
        print(f"note: git mv failed ({result.stderr.strip()}); falling back to a plain rename")
    source.rename(target)


def text_files() -> list[Path]:
    """Every UTF-8-decodable file under the root, bar git storage and build output."""
    found = []
    for path in sorted(ROOT.rglob("*")):
        if any(part in SKIP_DIRS for part in path.relative_to(ROOT).parts):
            continue
        if not path.is_file() or path.is_symlink():
            continue
        try:
            path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        found.append(path)
    return found


def trim_readme() -> bool:
    """Drop the template's half of `README.md`, up to and including the sentinel."""
    readme = ROOT / "README.md"
    if not readme.is_file():
        return False
    lines = readme.read_text(encoding="utf-8").splitlines(keepends=True)
    for index, line in enumerate(lines):
        if README_SENTINEL in line:
            kept = lines[index + 1 :]
            while kept and not kept[0].strip():
                kept.pop(0)
            readme.write_text("".join(kept), encoding="utf-8")
            return True
    return False


def main() -> int:
    if len(sys.argv) != 2:
        print(f"usage: python3 {Path(__file__).name} <Project>", file=sys.stderr)
        return 1

    new = sys.argv[1]
    if not NAME_RE.match(new):
        fail(f"{new!r} is not a valid Lean module name (letter first, then letters, digits, underscores)")
    if new == OLD:
        fail(f"the project is already named {OLD}; give the name it is becoming")

    old_lib, new_lib = ROOT / OLD, ROOT / new
    old_root, new_root = ROOT / f"{OLD}.lean", ROOT / f"{new}.lean"

    if not old_lib.is_dir() or not old_root.is_file():
        fail(f"{OLD}/ and {OLD}.lean are not both here---this checkout has already been renamed")
    if new_lib.exists() or new_root.exists():
        fail(f"{new}/ or {new}.lean already exists; refusing to overwrite")

    use_git = in_git_worktree()
    move(old_lib, new_lib, use_git)
    move(old_root, new_root, use_git)
    print(f"  {OLD}/ -> {new}/")
    print(f"  {OLD}.lean -> {new}.lean")

    if trim_readme():
        print("  trimmed README.md to the project's own half")

    script = Path(__file__).resolve()
    rewritten = []
    for path in text_files():
        if path == script:
            continue
        before = path.read_text(encoding="utf-8")
        after = before.replace(OLD, new)
        if after != before:
            path.write_text(after, encoding="utf-8")
            rewritten.append(path.relative_to(ROOT))
    for path in rewritten:
        print(f"  rewrote {path}")

    script.unlink()
    print(f"  removed {script.name}")

    print(f"\n{new} is renamed. Still to do, by hand:")
    print("  - fill in `description`, `keywords`, and `homepage` in lakefile.toml")
    print("  - delete the __docs__/ rules that do not apply, and record in CLAUDE.md which remain")
    print("  - replace the placeholders in README.md and CLAUDE.md")
    print("  - lake exe cache get && lake build")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
