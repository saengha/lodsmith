---
name: Good first recipe
about: Add a low-poly prop recipe (JSON + Build)
title: "feat(recipes): add "
labels:
  - good first issue
---

## Why this issue

A merged `id` is the public name Build and agents use (`lodsmith.<id>`, named parts, known `target_tris`). Pick something the catalog lacks. Near-duplicate crates will be closed. Examples of still-open names: see CONTRIBUTING.md. One recipe per first PR. Credit is CREDITS.md plus git, not a token.

## Prop

What should Build create? Check the README shipped list so you do not duplicate `crate`, `window`, `cart`, `well`, or `ladder`.

## Constraints

- Copy `recipes/crate.json` or run `python -m addon new recipe <id>`
- Filename `recipes/<id>.json` must equal `"id"`; reserved/troll ids are closed
- Separate named parts (unique lowercase slugs)
- `primitive` is `cube` until we document another type
- `target_tris` must be `12 ×` part count
- Optional `color` (`#RRGGBB`) and `tags`
- No cloud generator, no arbitrary `bpy` script

## Checklist

- [ ] I commented and tagged @saengha
- [ ] Conventional commit: `feat(recipes): add <id>`
- [ ] CREDITS.md line for my handle
- [ ] I did **not** have to edit Python, tests, or README for CI to pass
