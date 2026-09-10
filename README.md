# lodsmith

Local, recipe-driven **low-poly props** for indie games. You install a Blender add-on, pick `crate`, hit Build, and get named mesh parts with a known triangle budget — no cloud account, no `exec()` of arbitrary `bpy`.

## Why this exists

Most Blender + AI tools either let an agent run any Python in your scene, or pull a fused mesh from a hosted generator (Rodin, Tripo, Hunyuan). Indie pipelines need the opposite: **separate parts, predictable poly counts, GLB you can drop in a game**.

lodsmith starts as JSON recipes plus Blender operators. A local LLM planner can come later; today `lodsmith plan` is a keyword matcher that never leaves the machine. It is not a wrapper around those cloud mesh APIs.

## Why contribute

The useful indie vocabulary is small (tavern, warehouse, camp, smithy, inn) and the catalog is about **34 recipes / 11 sets**. A merged `id` is a public name. Build already creates `lodsmith.crate` with `crate.lid` (72 tris), plus names like `anvil.horn`, `bed.pillow`, `chair.back`. Agents type those same ids. The next careful name (`bellows`, `grindstone`, `wardrobe`) is claimed once. Kenney ships meshes you consume. Hosted generators ship a new unnamed mesh each prompt. Here you ship a **rebuildable recipe** — named cube parts, meters, `target_tris`. Don't exec bpy.

A first PR is one JSON file. You do not need Python. Near-duplicate crates and 1 cm-taller stools will be closed. Offensive or troll ids are closed by maintainers; CI also rejects reserved slugs. Credit is git plus [CREDITS.md](CREDITS.md), not a coin or a download counter. `plan` already accepts Korean (`선술집`, `모루`, `모닥불`, `의자`, `상자`); aliases for a new id are optional maintainer follow-up.

See [CONTRIBUTING.md](CONTRIBUTING.md).

## Install (Blender 4.2+)

1. Clone this repository.
2. In Blender: **Edit → Preferences → Get Extensions → Install from Disk** (or **Add-ons → Install** on older layouts) and select this folder — the one that contains `blender_manifest.toml`.
3. Enable **Lodsmith**.
4. 3D Viewport → sidebar (N) → **Lodsmith**. Type a prompt (`tavern`, `smithy`, `모루`, `모닥불`, `선술집`) → **Plan** or **Build prompt**. Or pick a single recipe → **Build**. **Validate** checks names and triangle count. **Export GLB** writes the active parent and its children.

You should get a parent like `lodsmith.crate` with named parts (floor, walls, lid) — not a single cube. Builds go in a `lodsmith` collection. Building the same recipe again replaces the previous parent. A set lands under `lodsmith.set.tavern`. **Snap Z to ground** keeps the 3D cursor’s XY and plants props at Z=0. **Clear lodsmith** deletes lodsmith objects. Build hides the factory `Cube` so a 0.8m crate is not swallowed by the 2m default mesh.

Shipped recipes: `crate`, `crate_open`, `crate_lid_ajar`, `crate_battens`, `barrel`, `barrel_open`, `pallet`, `bench`, `stool`, `table`, `lantern`, `fence_post`, `signpost`, `chest`, `mug`, `candle`, `sack`, `shelf`, `door`, `torch`, `bucket`, `window`, `ladder`, `cart`, `well`, `bed`, `chair`, `anvil`, `firepit`, `tent`, `bottle`, `book`, `hammer`, `cauldron`.

Shipped sets: `tavern`, `warehouse`, `yard`, `camp`, `market`, `entrance`, `crate_stack`, `wellside`, `facade`, `smithy`, `inn`.

## CLI (no Blender)

From the repo root:

```bash
python -m addon new recipe stool_tall --name "Tall stool"
python -m addon new set dock crate barrel pallet
python -m addon list
python -m addon sets
python -m addon validate
python -m addon compile crate
python -m addon compose tavern
python -m addon plan "wooden keg for a tavern"
python -m addon plan "선술집"
python -m addon plan "모루"
python -m addon plan "don't exec bpy"
```

`validate` is what CI runs. `compile` prints the scene graph JSON the Build operator consumes. `plan` ranks shipped recipes **and sets**; it does not call a model. Korean aliases (`선술집`, `모루`, `모닥불`, `의자`, `상자`) map onto the same catalog. `72 tris` and `don't exec bpy` rank the shipped crate — that is the budget and the rule, not a download counter.

## Add a recipe

```bash
python -m addon new recipe stool_tall --name "Tall stool"
```

Edit the JSON (`id` = filename, `target_tris` = `12 ×` part count), run `python -m addon validate` and `python -m pytest`, add a [CREDITS.md](CREDITS.md) line, open a PR, tag **@saengha**. You do not need to edit Python, planner synonyms, or the README shipped list. See [CONTRIBUTING.md](CONTRIBUTING.md).

## Free vs later (hosted)

| Layer | Status | What it is |
| --- | --- | --- |
| Recipes, sets, add-on, local build, GLB export, CLI | **Free, forever** | This repo. Apache-2.0. |
| Local LLM planner | Planned, OSS | Keyword `plan` / **Build prompt** is the stand-in. Still on-device. |
| Team recipe library, poly/naming gates, generation history | Later, hosted | Team ops. Individuals must still ship a game on OSS alone. |

Recipes will not be paywalled. The add-on will not require a login to Build.

## License

Apache License 2.0. See [LICENSE](LICENSE).
