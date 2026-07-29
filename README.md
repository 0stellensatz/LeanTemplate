# LeanTemplate

A GitHub template repository for a Lean 4 + Mathlib formalization project: the package `lake new <Project> math` produces, with a set of writing conventions and a structural checker already in position, and its Mathlib pin resolved so that `lake exe cache get` works on the first clone.

It is the seed for the Lean projects of a private notes repository, where each project derived from it is cloned back in as a git submodule. Nothing here is specific to that repository except a handful of paths in the conventions, noted at the end.

## Deriving a project from it

Everything down to the divider is about the template. `__rename__.py` cuts it in step 2, leaving the project's own README behind.

1. **Generate the repository**, public or private, and clone it where it belongs:

	```bash
	gh repo create <Owner>/<Project> --template 0stellensatz/LeanTemplate --private --clone
	```

2. **Rename the package.** A GitHub template copies files verbatim and substitutes nothing, so the package, the library directory, and the root all-import module are all still called `LeanTemplate`. One script does the whole rename and then deletes itself:

	```bash
	python3 __rename__.py <Project>
	```

	It renames the library directory and the root module, rewrites every textual occurrence of `LeanTemplate`, cuts this half of the README, and deletes itself. `__check__.py` is not rewritten and does not need to be: it takes the project name from the directory it sits in—so keep the checkout directory named after the package.

3. **Fill in `lakefile.toml`**—`description`, `keywords`, and `homepage`, which ship as placeholders. `[leanOptions]`, the Mathlib requirement, and its `rev` are already what a derived project wants; leave them alone unless the whole tree is moving to a new Mathlib.

4. **Prune `__docs__/` to the rules that actually apply**, and record in `CLAUDE.md` which ones remain. The template carries all four because a template cannot select; a project that does not follow a rule does not carry the document that states it. See *What ships* below.

5. **Write `README.md` and `CLAUDE.md`.** Both ship as skeletons with their placeholders marked. `AGENTS.md` is already a symlink to `CLAUDE.md`.

6. **Build it**, from the repository root:

	```bash
	lake exe cache get   # once, before the first build—otherwise Mathlib compiles from source
	lake build
	python3 __check__.py
	```

## What ships

- **`lakefile.toml`, `lean-toolchain`, `lake-manifest.json`, `.gitignore`**—what `lake new <Project> math` emits, on the toolchain named in `lean-toolchain` and with the Mathlib revision the manifest pins. The manifest is committed, which is what lets the first `lake exe cache get` land on prebuilt oleans instead of resolving the tag afresh and drifting off the revision the sibling projects are on.
- **`LeanTemplate.lean`**—the root all-import module, empty. Every source file added under `LeanTemplate/` gets its `import` line here in the same edit, or a plain `lake build` silently skips it. The exceptions are `Challenge.lean` and `CompareMathlib.lean`, which share `Development.lean`'s namespace and are built by name. The library directory beside it holds nothing but a `.gitkeep`, since git does not track an empty directory and `__check__.py` wants the directory to exist; delete it once there is a real source file.
- **`__check__.py`**—the structural checker. It is textual and needs no build, and it catches the mistakes a build does not report as errors: a file missing from the root module, a module that reaches two of a unit's three comparator files, and a comparator file that has drifted from its Challenge. For a project with no `Challenge.lean` only the root-import check applies.
- **`__docs__/`**—four convention documents, of which a project keeps only those it follows:
	- `rules-comments.md`—how the prose inside a comment is written. Applies to every project. Its closing *When the target is Mathlib* section is the conditional part: a project not aimed at upstreaming cuts it and says so in one line at the top, so the copy states only rules that are in force.
	- `rules-documentation.md`—module and declaration docstrings, and citations. Applies to every project; the citation section is worth narrowing per project.
	- `rules-formalization-project.md`—the `Defs.lean` / auxiliary-file architecture. Only for a project that formalizes a source unit by unit.
	- `rules-comparator.md`—the Challenge / Development pair. Only for a project that uses it; a project of exercise files or dated logs drops it.
- **`.github/workflows/build.yml`**—fetches the Mathlib cache, builds, builds any comparator files by name, and runs `__check__.py`. The three workflows `lake new` ships are deliberately not here: two of them publish releases and documentation, and the third opens automatic Mathlib-bump pull requests, which would break a tree that pins one Mathlib revision across every project.
- **`LICENSE`**—Apache-2.0, matching the Lean and Mathlib ecosystem. Replace it, or delete it, if the derived project wants something else.

Once derived, these are the project's own. They are fine-tuned in place as the project's reality demands, and an exception belongs in the project's copy, never back in the template. An edit to the template changes what the *next* project starts from; it does not reach the projects already derived, and propagating it into them is a deliberate, project-by-project act—a copy that has been fine-tuned is never overwritten wholesale.

## Paths that point outside

The conventions were written inside a private notes repository and refer to a few of its paths: `bib/__main__.bib` (the bibliography that docstring cite keys resolve against), `notes/math/theme/` (the reading notes behind a formalization), and `notes/code-lean4/` (where the derived projects are checked out). They do not resolve in a standalone clone. They are left in place because they record where a convention or a statement comes from, which is worth more than a path that resolves; a project used outside that repository repoints them in its own copies.

---

<!-- TEMPLATE-README-ENDS-HERE: `__rename__.py` deletes this line and everything above it, so what follows is all the derived project keeps. -->

# LeanTemplate

*What this project formalizes, and from which source. How it is laid out, unit by unit. What is proved and what is still open.*

## Building

Mathlib is pinned in `lake-manifest.json`, and `elan` will fetch the toolchain named in `lean-toolchain`. From this directory:

```bash
lake exe cache get   # once, before the first build—otherwise Mathlib compiles from source
lake build           # the whole project, by way of the root all-import module
python3 __check__.py
```

The conventions this project follows are its own copies, in `__docs__/`.
