# AGENTS.md

Instructions for coding agents working in this repository.

## Scope

- Prefer adding or editing a file under `recipes/`.
- Do not refactor `addon/` unless the change is required for a recipe to load or build.
- Do not add cloud mesh APIs (Rodin, Tripo, Hunyuan, Meshy, or similar).
- Do not add an operator that executes arbitrary Python or `bpy` from a model.
- Do not add payment, auth, or login gates around Build.
- Do not copy the MCPJam inspector monorepo layout into this repo.

## Layout

- `recipes/*.json` — contributor surface. Declarative parts, sizes, `target_tris`.
- `addon/recipe_loader.py` — pure Python; tested without Blender.
- `addon/operators/build_recipe.py` — `bpy` mesh build from a loaded recipe.
- `addon/ui/panel.py` — N-panel. Keep it thin.
- Tests live in `tests/` and must not import `bpy`.

## Checks

```bash
python -m pytest
```
