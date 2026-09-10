# lodsmith

Local, recipe-driven **low-poly props** for indie games. You install a Blender add-on, pick `crate`, hit Build, and get named mesh parts with a known triangle budget — no cloud account, no `exec()` of arbitrary `bpy`.

## Why this exists

Most Blender + AI tools either let an agent run any Python in your scene, or pull a fused mesh from a hosted generator (Rodin, Tripo, Hunyuan). Indie pipelines need the opposite: **separate parts, predictable poly counts, GLB you can drop in a game**.

lodsmith starts as JSON recipes plus Blender operators. A local LLM planner can come later. It is not a wrapper around those cloud mesh APIs.

## Install (Blender 4.2+)

1. Clone this repository.
2. In Blender: **Edit → Preferences → Get Extensions → Install from Disk** (or **Add-ons → Install** on older layouts) and select this folder — the one that contains `blender_manifest.toml`.
3. Enable **Lodsmith**.
4. 3D Viewport → sidebar (N) → **Lodsmith** → choose **Crate** → **Build**.

You should get an empty parent `lodsmith.crate` with body, walls, and a lid — not a single cube.

## Add a recipe

Copy [`recipes/crate.json`](recipes/crate.json), change `id` / `name` / `parts`, and open a PR. See [CONTRIBUTING.md](CONTRIBUTING.md).

## Free vs later (hosted)

| Layer | Status | What it is |
| --- | --- | --- |
| Recipes, add-on, local build | **Free, forever** | This repo. Apache-2.0. |
| Local LLM planner | Planned, OSS | Map a prompt onto an existing recipe. Still on-device. |
| GLB export | Planned, OSS | One-click export of the built prop. |
| Team recipe library, poly/naming gates, generation history | Later, hosted | Team ops. Individuals must still ship a game on OSS alone. |

Recipes will not be paywalled. The add-on will not require a login to Build.

## License

Apache License 2.0. See [LICENSE](LICENSE).
