# Architecture for source-formalization projects

These rules govern any Lake project that formalizes a piece of mathematical literature unit by unit—a *unit* being the project root itself, a book chapter (`CNN/`), or a paper section (`SNN/`), as fixed by the project's own `CLAUDE.md`. That `CLAUDE.md` also fixes the project's root namespace, its source of truth (the reading note under `notes/math/theme/` and/or the cached PDF), and any statement policy layered on top of these rules.

One companion document carries the part not repeated here: `./rules-documentation.md` (module and declaration docstrings, and citations).

A project that instead freezes its targets in a benchmark file and proves them in a parallel one—the Challenge / Development pair—is an auto-formalization project and starts from the template that carries those rules, not from this one.

## The project is a Lake package

Each project is a self-contained Lake package with its own `lakefile.toml`, `lean-toolchain`, `lake-manifest.json`, and (gitignored, machine-local) `.lake/`, held in a GitHub repository of its own and checked out under `notes/code-lean4/` as a git submodule. The sources sit in the library directory named after the project:

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

Module names mirror file paths under the package root: `<Project>/<Unit>/Foo.lean` is the module `<Project>.<Unit>.Foo`.

**The root module `<Project>.lean` directly imports every module of the project**, with no exceptions, so a plain `lake build` cannot silently omit a new file. Keep the import list sorted, and add to it whenever a module is added or renamed. This is the one thing `__check__.py` verifies, and it is verified because the failure is silent: a file left out of the list is not built, not type-checked, and reports nothing.

## Layout: one directory per unit

Each unit consists of:

- **`Defs.lean` — the unit's definitions:** structures, instances, notation, and `rfl`-level unfolding lemmas. Everything else in the unit imports it. It carries no `sorry`.
- **Auxiliary files `<Result>.lean`** — one per goal (or per tight cluster of goals), named in UpperCamelCase after the result proved, with the source tag recorded in the module docstring. This is where the actual multi-line proofs live, and the concluding lemma of such a file is the unit's public statement of that result: it is stated the way the source states it, in descriptive Mathlib style, and it is what a later unit imports.

That is the whole layout. A unit large enough that its directory listing stops being a usable index may add a summary module restating its results in the source's order and delegating to the auxiliary files—a convenience, not a requirement, and the project's `CLAUDE.md` says so if it keeps one.

Reading a unit in the source's order is otherwise the job of the module docstrings: each auxiliary file names the source item it discharges, so the tags are greppable even though the files are not ordered.

## Import discipline

Lean's import graph is acyclic, and the flow within a unit is fixed:

```
Defs.lean  ←  auxiliary files
```

- Auxiliary files import `Defs.lean`, and one another as needed. This is why the definitions sit in `Defs.lean` rather than in the file that first needs them: every auxiliary file must be able to state its lemmas over them.
- When a definition in `Defs.lean` carries a proof obligation, prove the obligation in place when it is short; if it grows, split it into a prerequisite auxiliary file imported *by* `Defs.lean`. Never leave a `sorry` in `Defs.lean`—a definition that does not elaborate takes everything downstream of it with it.
- Later units build on earlier ones by importing the earlier unit's modules directly.

## Workflow

1. **Skeleton.** Write `Defs.lean` from the source: the definitions the unit's results are stated over, and nothing else. Then create one auxiliary file per result, each stating its target and proving it by `sorry`. The unit must build at this stage—`sorry` is a warning, not an error—and the root module must already import every file created.
2. **Fill.** Pick a `sorry` and prove it, in the file where it is stated. An auxiliary file may carry `sorry`s while work on it is in progress; a lemma extracted along the way stays in the same file unless another file needs it, in which case it moves down to `Defs.lean` or to a prerequisite auxiliary file of its own.
3. **Settle the statement.** If the proof cannot be carried out as stated, the statement is what gets revisited—not quietly, in the same edit as the proof, but as its own change: fix the statement, say in the docstring how it now differs from the source's, and only then prove it. A statement that drifted to fit the proof that happened to be reachable is the failure this step exists to prevent, and there is nothing mechanical guarding against it here.

## Namespaces and naming

- Declarations live in the project's root namespace; source-level objects get nested namespaces for dot notation.
- Each auxiliary file wraps its contents in a sub-namespace named after the file (`namespace <Root>.RhoEP` inside `RhoEP.lean`); helpers not meant for use outside the file are `private`. The file's concluding lemma is the one other files reach for, so it is the one whose name is worth arguing about.
- Docstrings on source-facing declarations cite the source's numbering and page, matching the reading note—see `./rules-documentation.md`.
- Modeling decisions (how a source object is encoded—e.g. `ℤ_{≥1}` as `ℕ+`) are recorded once, in the `## Implementation notes` of the `Defs.lean` that introduces them, and stay consistent across units.
- When a declaration's natural name collides with the Mathlib lemma it mirrors, the Mathlib one is reachable as `_root_.<name>`; prefer a distinct descriptive name when the collision would confuse.

## File layout

Every `.lean` file starts with `import Mathlib`, then the project-local imports (each on its own line), then the module docstring:

```lean
import Mathlib
import <Project>.<Unit>.Defs

/-!
# <title>
...
-/
```

**There is no file-level `set_option` block.** The suppressions this tree used to open every file with—`warningAsError false`, `linter.style.longLine false`, `linter.style.emptyLine false`—are gone, and the set is empty: nothing stands between a file and the Mathlib linter set that `lakefile.toml` enables. The long-line linter in particular is now a check the file is expected to pass, since comments are hard-wrapped at 100 columns (`./rules-comments.md`).

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
lake build                          # the whole project, by way of the root all-import module
lake build <Project>.<Unit>.<File>  # one file and its dependencies
```

A fresh checkout of a project needs `lake exe cache get` **before** the first build—otherwise Lean compiles Mathlib from source, which takes hours. Alongside the build, run the project's own structural check:

```bash
python3 __check__.py
```

The toolchain and the remaining `lake` commands are documented in the project's own `README.md`, one directory up from this one.
