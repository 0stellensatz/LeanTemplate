# Architecture for source-formalization projects

These rules govern any Lake project that formalizes a piece of mathematical literature unit by unit—a *unit* being whatever slice of the source the project chooses to work in, as fixed by the project's own `CLAUDE.md`: a chapter, a section, one theorem together with the lemmas it needs, or the project root itself when the source is short enough not to want dividing. Nothing below depends on which of those it is, on how a unit's directory is named, or on whether a unit gets a directory at all.

That `CLAUDE.md` also fixes the project's root namespace, its source of truth (the paper, a reading note taken from it, or both), and any statement policy layered on top of these rules.

One companion document carries the part not repeated here: `./rules-documentation.md` (module and declaration docstrings, and citations).

A project that instead freezes its targets in a benchmark file and proves them in a parallel one—the Challenge / Development pair—is an auto-formalization project and starts from the template that carries those rules, not from this one.

## The project is a Lake package

Each project is a self-contained Lake package with its own `lakefile.toml`, `lean-toolchain`, `lake-manifest.json`, and (gitignored, machine-local) `.lake/`, held in a repository of its own. The sources sit in the library directory named after the project:

```
<Project>/
├── lakefile.toml   lean-toolchain   lake-manifest.json   .gitignore
├── README.md   CLAUDE.md   AGENTS.md → CLAUDE.md
├── __docs__/            the project's own copies of the rules it follows
├── __check__.py         the project's own copy of the structural checker
├── <Project>.lean       the root all-import module
└── <Project>/           the library source tree
```

The `__docs__/` copies and `__check__.py` arrive with the template repository the project is generated from, and are the project's own from then on: they are fine-tuned in place to fit it, and a project keeps only the rules that apply to it, deleting the rest.

Module names mirror file paths under the package root: `<Project>/<Path>/Foo.lean` is the module `<Project>.<Path>.Foo`.

**The root module `<Project>.lean` directly imports every module of the project**, with no exceptions, so a plain `lake build` cannot silently omit a new file. Keep the import list sorted, and add to it whenever a module is added or renamed. This is the one thing `__check__.py` verifies, and it is verified because the failure is silent: a file left out of the list is not built, not type-checked, and reports nothing.

Nothing else about the layout is fixed. How a unit is spelled on disk—a directory of its own, a flat run of files at the library root, one file—is the project's decision, recorded in its `CLAUDE.md`, and neither the build nor the checker has an opinion about it.

## What a unit holds

Two kinds of thing, and how many files they take is again the project's choice:

- **The definitions** the unit's results are stated over: structures, instances, notation, and `rfl`-level unfolding lemmas. Give them a file of their own—`Defs.lean` is the conventional name, and nothing enforces it—as soon as more than one file states lemmas over them, so that each of those files can import the definitions rather than one of them owning the definitions and the rest having to import it whole. A unit with one proof file, or one whose results are stated in Mathlib's vocabulary alone, wants no such file.
- **The proofs.** One file per goal, or per tight cluster of goals, named in UpperCamelCase after the result proved, with the source tag recorded in the module docstring. The concluding declaration of such a file is the unit's public statement of that result: stated the way the source states it, in descriptive Mathlib style, and it is what a later unit imports.

A unit large enough that its file listing stops being a usable index may add a summary module restating its results in the source's order and delegating to the proof files—a convenience, not a requirement, and the project's `CLAUDE.md` says so if it keeps one.

Reading a unit in the source's order is otherwise the job of the module docstrings: each file names the source item it discharges, so the tags are greppable even though the files are not ordered.

## Import discipline

Lean's import graph is acyclic, and a unit's shape follows from that: the definitions at the bottom, the proofs above them, nothing reaching back down.

- A file that states lemmas over the unit's definitions imports wherever those definitions live. That is the argument for giving them a file of their own once there are two such files: without it, one proof file owns the definitions and every sibling has to import that file whole, dragging its proofs into scope along with them.
- When a definition carries a proof obligation, prove the obligation in place when it is short; if it grows, split it into a prerequisite file imported *by* the one holding the definition. Never leave a `sorry` underneath a definition—a definition that does not elaborate takes everything downstream of it with it.
- Later units build on earlier ones by importing the earlier unit's modules directly.

## Workflow

1. **Skeleton.** Write the unit's definitions from the source, and nothing else yet. Then state each of its results where it will be proved, each by `sorry`. The unit must build at this stage—`sorry` is a warning, not an error—and the root module must already import every file created.
2. **Fill.** Pick a `sorry` and prove it, in the file where it is stated. A file may carry `sorry`s while work on it is in progress; a lemma extracted along the way stays in the same file unless another file needs it, in which case it moves down to the definitions or to a prerequisite file of its own.
3. **Settle the statement.** If the proof cannot be carried out as stated, the statement is what gets revisited—not quietly, in the same edit as the proof, but as its own change: fix the statement, say in the docstring how it now differs from the source's, and only then prove it. A statement that drifted to fit the proof that happened to be reachable is the failure this step exists to prevent, and there is nothing mechanical guarding against it here.

## Namespaces and naming

- Declarations live in the project's root namespace; source-level objects get nested namespaces for dot notation.
- Each file wraps its contents in a sub-namespace named after it (`namespace <Root>.RhoEP` inside `RhoEP.lean`); helpers not meant for use outside the file are `private`. The file's concluding declaration is the one other files reach for, so it is the one whose name is worth arguing about.
- Docstrings on source-facing declarations cite the source's numbering and page—see `./rules-documentation.md`.
- Modeling decisions (how a source object is encoded—e.g. `ℤ_{≥1}` as `ℕ+`) are recorded once, in the `## Implementation notes` of the file that introduces the definition they concern, and stay consistent across units.
- When a declaration's natural name collides with the Mathlib lemma it mirrors, the Mathlib one is reachable as `_root_.<name>`; prefer a distinct descriptive name when the collision would confuse.

## File layout

Every `.lean` file starts with `import Mathlib`, then the project-local imports (each on its own line), then the module docstring:

```lean
import Mathlib
import <Project>.<Path>.Defs

/-!
# <title>
...
-/
```

**There is no file-level `set_option` block.** The suppressions it is tempting to open every file with—`warningAsError false`, `linter.style.longLine false`, `linter.style.emptyLine false`—are not used, and the set is empty: nothing stands between a file and the Mathlib linter set that `lakefile.toml` enables. The long-line linter in particular is a check the file is expected to pass, since comments are hard-wrapped at 100 columns (`./rules-comments.md`).

A `set_option` that changes *elaboration* rather than silencing a linter is a different matter and stays available—but only in the scoped form, attached to the one declaration that needs it and carrying a comment saying why:

```lean
set_option maxHeartbeats 1000000 in
-- The instance search for `IsDedekindDomain (integers L)` is the expensive step.
theorem foo : ... := ...
```

This is what Mathlib's own `linter.style.setOption` demands; an unscoped `set_option maxHeartbeats` at the top of a file is reported by it.

## Building

All of these are run from the project directory (from elsewhere, wrap the change of directory in a subshell so it does not leak into later commands):

```bash
lake build                            # the whole project, by way of the root all-import module
lake build <Project>.<Path>.<Module>  # one module and its dependencies
lake env lean <Project>/<Path>/<Module>.lean   # type-check a single file
```

A fresh checkout of a project needs `lake exe cache get` **before** the first build—otherwise Lean compiles Mathlib from source, which takes hours. Alongside the build, run the project's own structural check:

```bash
python3 __check__.py
```

The toolchain and the remaining `lake` commands are documented in the project's own `README.md`, one directory up from this one.
