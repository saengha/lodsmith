"""Check the active lodsmith prop or set against its recipe budgets."""

from __future__ import annotations

import bpy

from ..compile import compile_recipe
from ..naming import recipe_id_from_parent
from ..recipe_loader import RecipeError, load_all, recipes_dir
from .spawn import mesh_tris


class LODSMITH_OT_validate_prop(bpy.types.Operator):
    bl_idname = "lodsmith.validate_prop"
    bl_label = "Validate"
    bl_description = "Compare the active lodsmith prop or set to its recipes"
    bl_options = {"REGISTER"}

    def execute(self, context):
        active = context.view_layer.objects.active
        set_root = _set_root(active)
        if set_root is not None:
            return _validate_set(self, set_root)

        parent = _lodsmith_parent(active)
        if parent is None:
            self.report({"ERROR"}, "Select a lodsmith prop or set")
            return {"CANCELLED"}
        return _validate_one(self, parent)


def _validate_one(operator, parent):
    recipe_id = parent.get("lodsmith_recipe_id") or recipe_id_from_parent(parent.name)
    if not recipe_id:
        operator.report({"ERROR"}, f"Not a lodsmith parent: {parent.name}")
        return {"CANCELLED"}
    try:
        recipes = {recipe.id: recipe for recipe in load_all(recipes_dir())}
    except RecipeError as exc:
        operator.report({"ERROR"}, str(exc))
        return {"CANCELLED"}
    recipe = recipes.get(recipe_id)
    if recipe is None:
        operator.report({"ERROR"}, f"Unknown recipe: {recipe_id}")
        return {"CANCELLED"}

    compiled = compile_recipe(recipe)
    problems = _prop_problems(parent, compiled)
    if problems:
        operator.report({"ERROR"}, f"{parent.name}: " + "; ".join(problems))
        return {"CANCELLED"}
    operator.report(
        {"INFO"},
        f"{parent.name}: {len(compiled.parts)} parts, "
        f"{compiled.target_tris} tris — ok",
    )
    return {"FINISHED"}


def _validate_set(operator, root):
    try:
        recipes = {recipe.id: recipe for recipe in load_all(recipes_dir())}
    except RecipeError as exc:
        operator.report({"ERROR"}, str(exc))
        return {"CANCELLED"}
    children = [child for child in root.children if child.get("lodsmith_recipe_id")]
    if not children:
        operator.report({"ERROR"}, f"{root.name}: no recipe children")
        return {"CANCELLED"}
    failed = []
    total = 0
    for child in children:
        recipe = recipes.get(child.get("lodsmith_recipe_id"))
        if recipe is None:
            failed.append(f"{child.name}: unknown recipe")
            continue
        compiled = compile_recipe(recipe)
        problems = _prop_problems(child, compiled)
        total += compiled.target_tris
        if problems:
            failed.append(f"{child.name}: {'; '.join(problems)}")
    if failed:
        operator.report({"ERROR"}, f"{root.name}: " + " | ".join(failed[:4]))
        return {"CANCELLED"}
    operator.report(
        {"INFO"},
        f"{root.name}: {len(children)} props, {total} tris — ok",
    )
    return {"FINISHED"}


def _prop_problems(parent, compiled) -> list[str]:
    got = {
        child.get("lodsmith_part") or child.name.rsplit(".", 1)[-1]
        for child in parent.children
        if child.type == "MESH"
    }
    expected = {part.part_name for part in compiled.parts}
    problems = []
    missing = sorted(expected - got)
    extra = sorted(got - expected)
    tris = sum(mesh_tris(child) for child in parent.children)
    if missing:
        problems.append(f"missing {', '.join(missing)}")
    if extra:
        problems.append(f"extra {', '.join(extra)}")
    if tris != compiled.target_tris:
        problems.append(f"tris {tris} != target {compiled.target_tris}")
    return problems


def _set_root(obj):
    current = obj
    while current is not None:
        if current.get("lodsmith_set_id") or current.name.startswith("lodsmith.set."):
            return current
        current = current.parent
    return None


def _lodsmith_parent(obj):
    current = obj
    while current is not None:
        recipe_id = current.get("lodsmith_recipe_id")
        if recipe_id or recipe_id_from_parent(current.name):
            return current
        current = current.parent
    return None
