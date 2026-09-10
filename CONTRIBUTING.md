# Contributing

The unit of contribution is a **JSON recipe or set**. You do not need to touch Python.

Your merged `id` becomes `lodsmith.<id>` with named parts (`crate.lid`, 72 tris on the shipped crate). That is the credit: a name agents Build and a game can select. We do not issue tokens, paid slots, or fake founder badges. Don't exec bpy. The IKEA step is `python -m addon new recipe <id>` — then you own the parts.

The useful tavern / warehouse / camp / smithy vocabulary is finite. About 34 recipes exist. A careful new prop is a first PR; a pile of near-copies is not. `crate.lid` and `anvil.horn` are taken.

## Names that get closed

A merged `id` is public (`lodsmith.<id>`, named parts like `crate.lid`). Offensive, sexual, hate, impersonation, and troll ids are **closed without debate**. Near-duplicate spam (`crate2`, a 1 cm-taller stool) is closed the same way.

Comments on an issue or PR can flag a bad name. **Only maintainers merge.** Other contributors do not get vigilante close or merge powers.

CI (`python -m addon validate`, pytest) rejects reserved and blocked slugs (`cube`, `untitled`, `test`, and a short troll list). The denylist in `addon/naming.py` is short on purpose. Maintainers can still close anything the list misses.

## First PR

```bash
git clone https://github.com/YOUR_USERNAME/lodsmith.git
cd lodsmith
python -m pip install pytest
python -m addon new recipe stool_tall --name "Tall stool"
# edit recipes/stool_tall.json — keep id == filename, target_tris == 12 × parts
python -m addon validate
python -m pytest
# same PR: one line in CREDITS.md — `stool_tall` — @yourhandle
```

Open a PR titled `feat(recipes): add stool_tall` and tag **@saengha**. Comment on an issue first if you can. One recipe (or one set) per first PR.

A set is the same shape:

```bash
python -m addon new set dock crate barrel pallet
```

## Rules that fail CI

- `"id"` equals the filename stem (`stool_tall.json`)
- `id` is a lowercase slug and is not reserved/blocked (`addon/naming.py`)
- Recipes: `primitive` is `cube`, unique lowercase part names, `target_tris` is `12 * len(parts)`
- Sets: every `items[].recipe` already exists in `recipes/`
- No cloud mesh APIs, no arbitrary `bpy` from a model, no login gate on Build

Planner synonyms, Korean aliases, and README lists are optional. Maintainers can add those after merge.

## Quality

- Parts a programmer can select (`lid`, `horn`, not `cube_07`)
- Sizes in meters at indie scale (shipped `crate` is 0.8 × 0.6 × ~0.5 m)
- New silhouette or function, not a rename of `crate` / `stool`
- Sets may only reference recipes that already exist in `recipes/`

## Names still open (examples, not a quota)

Comment first. These are not bounties and not a promise we will merge a thin cube stack. Claimed this round: `bed`, `chair`, `anvil`, `firepit`, `tent`, `bottle`, `book`, `hammer`, `cauldron`, plus sets `smithy` and `inn`.

Recipes still unnamed: `bellows`, `grindstone`, `wardrobe`.

Sets that can land on **shipped** recipes only, e.g. `dock` (`crate`, `barrel`, `pallet`). Do not reship `tavern` as another pub corner.

## What not to send

- Rodin / Tripo / Hunyuan / Meshy wrappers
- An operator that `exec`s model-written Python
- Payment, accounts, or tokens that lock Build
- Coins, whitelist access, fake download counts, countdown “slots”
- Catalog spam (third lid angle, 1 cm-taller stool, 40 untitled boxes)
- Offensive, sexual, hate, impersonation, or joke/troll ids (`lodsmith.<id>` is the public API)

Tag **@saengha** on the issue or pull request.
