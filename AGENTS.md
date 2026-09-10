# AGENTS.md

Instructions for coding agents working in this repository.

## Scope

- Prefer adding or editing a file under `recipes/` or `sets/`.
- New recipe: a valid `recipes/<id>.json` is enough (`python -m addon new recipe <id>`). Planner synonyms, Korean aliases, and README lists are optional maintainer follow-up.
- Recipe/set ids must pass `addon/naming.py` (lowercase slug plus a short reserved/blocked list). Offensive or troll ids are closed by maintainers even if CI misses them.
- New set: a valid `sets/<id>.json` is enough (`python -m addon new set <id> crate barrel`).
- Do not refactor `addon/` unless the change is required for a recipe or set to load or build.
- Do not add cloud mesh APIs (Rodin, Tripo, Hunyuan, Meshy, or similar).
- Do not add an operator that executes arbitrary Python or `bpy` from a model.
- Do not add payment, auth, or login gates around Build.
- Do not add tokens, coins, fake download counts, or countdown scarcity.
- Do not copy the MCPJam inspector monorepo layout into this repo.

## Layout

- `recipes/*.json` — contributor surface. Declarative parts, sizes, `target_tris`, optional `color` / `tags`.
- `sets/*.json` — several recipes with locations. `repeat` tiles a prop.
- `recipes/recipe.schema.json` / `sets/set.schema.json` — documentation; loaders skip `*.schema.json`.
- `addon/recipe_loader.py` — pure Python; tested without Blender.
- `addon/set_loader.py` — set JSON.
- `addon/compile.py` — bpy-free scene graph the Build operator consumes.
- `addon/planner.py` — local keyword ranking, including Korean aliases. Not an LLM.
- `addon/cli.py` — `python -m addon …`
- `addon/naming.py` — slug + short reserved/blocked list for catalog ids.
- `addon/operators/build_recipe.py` — `bpy` mesh build from a compiled recipe.
- `addon/operators/build_prompt.py` — plan + build at the 3D cursor.
- `addon/ui/panel.py` — N-panel. Keep it thin.
- Tests live in `tests/` and must not import `bpy`.

## Checks

```bash
python -m pytest
python -m addon validate
```
