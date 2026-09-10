# Contributing

Thanks for considering a change. The unit of contribution is a **recipe**, not a new architecture.

## Before you start

1. Comment on an issue (or open one) and tag **@saengha** so two people do not build the same prop.
2. Look for `good first issue`. Adding `barrel.json` is the intended starter.

## Setup

```bash
git clone https://github.com/YOUR_USERNAME/lodsmith.git
cd lodsmith
python -m pip install pytest
python -m pytest
```

Install the repo folder as a Blender 4.2+ extension to click **Build** in the viewport.

## Add a recipe

1. Copy `recipes/crate.json` to `recipes/<id>.json`.
2. Set a unique `id` (filename without `.json`), a display `name`, and `target_tris`.
3. List `parts` with `name`, `primitive` (`cube` only for now), `size` `[x, y, z]`, and `location` `[x, y, z]`.
4. Keep parts separate (body / lid / walls). Do not collapse into one blob.
5. Run `python -m pytest`.
6. Open a pull request.

## Commit messages

[Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/):

```
feat(recipes): add barrel
fix(loader): reject empty parts lists
```

## What not to send

- Cloud mesh APIs (Rodin, Tripo, Hunyuan, …)
- Arbitrary `bpy` script execution from the LLM
- Refactors of the panel / loader unless a recipe cannot ship without them
- Payment, accounts, or feature flags that lock Build behind a login

## Help

Tag **@saengha** on the issue or pull request.
