"""Spawn compiled recipes into the lodsmith collection. bpy only."""

from __future__ import annotations

import math

import bpy

from ..colors import hex_to_rgb
from ..compile import CompiledPart, compile_recipe
from ..recipe_loader import Recipe
from ..set_loader import PropSet
from .mesh_factory import new_cube_object

COLLECTION_NAME = "lodsmith"


def lodsmith_collection(context):
    col = bpy.data.collections.get(COLLECTION_NAME)
    if col is None:
        col = bpy.data.collections.new(COLLECTION_NAME)
    scene_col = context.scene.collection
    if col.name not in scene_col.children:
        try:
            scene_col.children.link(col)
        except RuntimeError:
            pass
    return col


def cursor_origin(context) -> tuple[float, float, float]:
    cursor = getattr(context.scene, "cursor", None)
    if cursor is None:
        location = (0.0, 0.0, 0.0)
    else:
        loc = cursor.location
        location = (float(loc[0]), float(loc[1]), float(loc[2]))
    if getattr(context.scene, "lodsmith_on_ground", True):
        return (location[0], location[1], 0.0)
    return location


def remove_object_tree(name: str) -> None:
    existing = bpy.data.objects.get(name)
    if existing is None:
        return
    victims = [existing, *existing.children_recursive]
    for obj in victims:
        bpy.data.objects.remove(obj, do_unlink=True)


def is_lodsmith_object(obj) -> bool:
    if obj is None:
        return False
    return bool(
        obj.name.startswith("lodsmith.")
        or obj.get("lodsmith_recipe_id")
        or obj.get("lodsmith_set_id")
        or obj.get("lodsmith_part")
    )


def clear_lodsmith_objects() -> int:
    roots = [
        obj
        for obj in list(bpy.data.objects)
        if is_lodsmith_object(obj)
        and not is_lodsmith_object(obj.parent)
    ]
    count = len(roots)
    for root in roots:
        remove_object_tree(root.name)
    return count


def spawn_recipe(
    context,
    recipe: Recipe,
    *,
    root_name: str,
    origin: tuple[float, float, float],
    parent=None,
    replace: bool = False,
    rotation_deg: tuple[float, float, float] = (0.0, 0.0, 0.0),
    scale: float = 1.0,
):
    compiled = compile_recipe(recipe)
    if replace:
        remove_object_tree(root_name)

    collection = lodsmith_collection(context)
    root = bpy.data.objects.new(root_name, None)
    collection.objects.link(root)
    if parent is not None:
        root.parent = parent
    root.location = origin
    root.rotation_euler = tuple(math.radians(angle) for angle in rotation_deg)
    root.scale = (scale, scale, scale)
    root["lodsmith_recipe_id"] = compiled.recipe_id
    root["lodsmith_target_tris"] = compiled.target_tris

    created = []
    for part in compiled.parts:
        obj = new_cube_object(
            collection,
            f"{root_name}.{part.part_name}",
            part.size,
            (0.0, 0.0, 0.0),
            part.rotation_deg,
        )
        obj.parent = root
        obj.location = part.location
        obj["lodsmith_part"] = part.part_name
        assign_color(obj, part)
        created.append(obj)
    return root, created


def spawn_set(context, prop_set: PropSet, catalog: dict[str, Recipe], origin):
    set_name = f"lodsmith.set.{prop_set.id}"
    remove_object_tree(set_name)
    collection = lodsmith_collection(context)
    root = bpy.data.objects.new(set_name, None)
    collection.objects.link(root)
    root.location = origin
    root["lodsmith_set_id"] = prop_set.id
    created = [root]
    counts: dict[str, int] = {}
    for item in prop_set.items:
        recipe = catalog[item.recipe_id]
        counts[recipe.id] = counts.get(recipe.id, 0) + 1
        index = counts[recipe.id] - 1
        child_name = f"{prop_set.id}.{recipe.id}_{index:02d}"
        child, parts = spawn_recipe(
            context,
            recipe,
            root_name=child_name,
            origin=item.location,
            parent=root,
            replace=False,
            rotation_deg=item.rotation_deg,
            scale=item.scale,
        )
        created.extend(parts)
        created.append(child)
    return root, created


def assign_color(obj, part: CompiledPart) -> None:
    if not part.color:
        return
    mat = color_material(part.color)
    if obj.data.materials:
        obj.data.materials[0] = mat
    else:
        obj.data.materials.append(mat)


def color_material(color_hex: str):
    mat_name = f"lodsmith.col.{color_hex.lstrip('#')}"
    mat = bpy.data.materials.get(mat_name)
    if mat is None:
        mat = bpy.data.materials.new(mat_name)
    rgb = hex_to_rgb(color_hex)
    mat.diffuse_color = (*rgb, 1.0)
    mat.use_nodes = True
    bsdf = None
    for node in mat.node_tree.nodes:
        if node.type == "BSDF_PRINCIPLED":
            bsdf = node
            break
    if bsdf is not None:
        if "Base Color" in bsdf.inputs:
            bsdf.inputs["Base Color"].default_value = (*rgb, 1.0)
        if "Roughness" in bsdf.inputs:
            bsdf.inputs["Roughness"].default_value = 1.0
        if "Metallic" in bsdf.inputs:
            bsdf.inputs["Metallic"].default_value = 0.0
    return mat


def select_tree(context, root, extras) -> None:
    for obj in context.view_layer.objects:
        obj.select_set(False)
    for obj in extras:
        obj.select_set(True)
    root.select_set(True)
    context.view_layer.objects.active = root


def mesh_tris(obj) -> int:
    mesh = getattr(obj, "data", None)
    if mesh is None or not hasattr(mesh, "calc_loop_triangles"):
        return 0
    mesh.calc_loop_triangles()
    return len(mesh.loop_triangles)
