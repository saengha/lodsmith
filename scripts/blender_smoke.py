"""Headless Build → Validate → Export against the same blender.exe the user has open."""

from __future__ import annotations

import sys
import tempfile
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT.parent))

import bpy

import lodsmith
from lodsmith.addon.compile import compile_recipe
from lodsmith.addon.recipe_loader import load_all, recipes_dir


def _fail(message: str) -> None:
    print(f"SMOKE_FAIL {message}", flush=True)
    raise SystemExit(1)


def _mesh_tris(obj) -> int:
    mesh = getattr(obj, "data", None)
    if mesh is None or not hasattr(mesh, "calc_loop_triangles"):
        return 0
    mesh.calc_loop_triangles()
    return len(mesh.loop_triangles)


def main() -> int:
    print("BLENDER_VERSION", bpy.app.version_string, flush=True)
    lodsmith.register()

    recipes = load_all(recipes_dir())
    if not recipes:
        _fail("no recipes loaded")

    sample_ids = ["crate", "barrel", "lantern", "chest", "window"]
    for recipe_id in sample_ids:
        result = bpy.ops.lodsmith.build_recipe(recipe_id=recipe_id)
        if result != {"FINISHED"}:
            _fail(f"build {recipe_id}: {result}")
        parent = bpy.data.objects.get(f"lodsmith.{recipe_id}")
        if parent is None:
            _fail(f"missing parent lodsmith.{recipe_id}")
        recipe = next(item for item in recipes if item.id == recipe_id)
        compiled = compile_recipe(recipe)
        got = {
            child.get("lodsmith_part")
            for child in parent.children
            if child.type == "MESH"
        }
        expected = {part.part_name for part in compiled.parts}
        if got != expected:
            _fail(f"{recipe_id} parts {got} != {expected}")
        tris = sum(_mesh_tris(child) for child in parent.children)
        if tris != compiled.target_tris:
            _fail(f"{recipe_id} tris {tris} != {compiled.target_tris}")
        validate = bpy.ops.lodsmith.validate_prop()
        if validate != {"FINISHED"}:
            _fail(f"validate {recipe_id}: {validate}")
        print(
            f"SMOKE_OK build {recipe_id} parts={len(compiled.parts)} tris={tris}",
            flush=True,
        )

    bpy.context.scene.lodsmith_prompt = "tavern"
    planned = bpy.ops.lodsmith.plan_prompt()
    if planned != {"FINISHED"}:
        _fail(f"plan tavern: {planned}")
    built = bpy.ops.lodsmith.build_prompt()
    if built != {"FINISHED"}:
        _fail(f"build prompt tavern: {built}")
    tavern = bpy.data.objects.get("lodsmith.set.tavern")
    if tavern is None:
        _fail("missing lodsmith.set.tavern")
    prop_count = sum(1 for child in tavern.children if child.get("lodsmith_recipe_id"))
    if prop_count < 8:
        _fail(f"tavern props {prop_count}")
    print(f"SMOKE_OK set tavern props={prop_count}", flush=True)
    tavern_validate = bpy.ops.lodsmith.validate_prop()
    if tavern_validate != {"FINISHED"}:
        _fail(f"validate tavern set: {tavern_validate}")
    print("SMOKE_OK validate tavern set", flush=True)
    if "lodsmith" not in bpy.data.collections:
        _fail("missing lodsmith collection")

    crate = bpy.data.objects["lodsmith.crate"]
    for obj in bpy.context.view_layer.objects:
        obj.select_set(False)
    crate.select_set(True)
    for child in crate.children_recursive:
        child.select_set(True)
    bpy.context.view_layer.objects.active = crate

    out = Path(tempfile.gettempdir()) / "lodsmith_smoke_crate.glb"
    if out.exists():
        out.unlink()
    exported = bpy.ops.lodsmith.export_glb(filepath=str(out))
    if exported != {"FINISHED"}:
        _fail(f"export: {exported}")
    size = out.stat().st_size
    if size < 200:
        _fail(f"glb too small: {size} bytes")
    print(f"SMOKE_OK export {out} bytes={size}", flush=True)

    lodsmith.unregister()
    print("SMOKE_PASS", flush=True)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except SystemExit:
        raise
    except Exception:
        traceback.print_exc()
        raise SystemExit(1)
