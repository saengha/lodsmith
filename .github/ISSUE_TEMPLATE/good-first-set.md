---
name: Good first set
about: Arrange shipped recipes into a set (JSON + Build set)
title: "feat(sets): add "
labels:
  - good first issue
---

## Why this issue

A merged set `id` is what **Build set** and `plan` rank (`lodsmith.set.dock`). Every `items[].recipe` must already be shipped — land a missing recipe first. Arrange a scene, do not dump every prop. One set per first PR. Credit is CREDITS.md plus git, not a token.

## Set

What should **Build set** create? Check the README shipped sets so you do not duplicate `tavern`, `crate_stack`, `wellside`, or `facade`.

## Constraints

- Copy `sets/tavern.json` or run `python -m addon new set <id> crate barrel`
- Filename `sets/<id>.json` must equal `"id"`; reserved/troll ids are closed
- Every `items[].recipe` must already be shipped
- Optional `repeat` + `offset` tiles a prop (see `yard` and `crate_stack`)
- No cloud generator, no arbitrary `bpy` script

## Checklist

- [ ] I commented and tagged @saengha
- [ ] Conventional commit: `feat(sets): add <id>`
- [ ] CREDITS.md line for my handle
- [ ] I did **not** have to edit Python, tests, or README for CI to pass
