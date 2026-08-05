# CLAUDE.md

This file provides guidance to coding agents—Claude Code (claude.ai/code) and Codex alike—when working with code in this directory. It is surfaced to Codex as `AGENTS.md` through a symlink, so keep the guidance tool-neutral.

**This is still the template's skeleton.** Every section below is to be rewritten for the project derived from it; the placeholders say what each one has to end up recording. Delete this paragraph when they are all filled in.

## Project

*What the project formalizes.* If it is bound to a source, name the work and its cite key in `bib/__main__.bib` (repo-root-relative); if it is bound to a theorem rather than to a paper, state the theorem and say that the exposition is not being followed step by step. Name the source of truth for statements—a reading note under `notes/math/theme/`, the cached PDF, or both—and the form a page or theorem citation takes.

## Architecture

This is a standalone Lake package. *Whether it follows `@./__docs__/rules-formalization-project.md`*—the `Defs.lean` / auxiliary-file architecture, unit by unit—and if so, the project-specific parameters that document leaves open:

- **The unit granularity**: whether a unit is the project root itself, a chapter directory `CNN/`, or a section directory `SNN/`—and so what the module names and the build target look like.
- **The root namespace**, and whether the project declares one flat namespace or a sub-namespace per file.
- **Where the definitional layer lives**: `Defs.lean` per unit, one shared file, or nothing so heavy that it wants a file of its own.
- **Whether the project keeps a per-unit summary module** restating that unit's results in the source's order, and what it is called.
- **Whether Mathlib may be used without restriction**, or whether the project draws a preliminary boundary that later units must respect.
- **Any standing exemption**—an unused-variable warning kept on purpose, an unscoped `maxHeartbeats`—with the reasoning recorded in the `__docs__/` copy that governs it, not here.

Every source file must be reachable from the root all-import module `LeanTemplate.lean`; adding a `.lean` file means adding its `import` line there in the same edit. There are no exceptions, and `__check__.py` is what enforces it.

## Which rules this project carries

*Which documents survived the prune, and what was changed in them.* The template ships three in `__docs__/`—`rules-comments.md`, `rules-documentation.md`, `rules-formalization-project.md`—plus the structural checker `__check__.py`. A project that does not follow a rule deletes the document that states it; a project whose situation differs from the generic wording edits its own copy rather than having the wording carve out an exception.

The one edit almost every project makes: `rules-comments.md` closes with a *When the target is Mathlib* section, which a project not aimed at upstreaming cuts, noting the cut in one line at the top of its copy.

These copies are this project's own and are fine-tuned here, not in the template. Run the checker before declaring work done, and a build after it:

```bash
python3 __check__.py
lake build
```

## Editing conventions for the comments

Follow the rules in @./__docs__/rules-comments.md for Markdown-styled comments across the files, and @./__docs__/rules-documentation.md for the module docstrings, the per-declaration docstrings, and the citations.
