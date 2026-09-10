"""Plan a prompt onto recipes/sets, then Build the top hit at the 3D cursor."""

from __future__ import annotations

import bpy

from ..naming import parent_name
from ..planner import plan
from ..recipe_loader import RecipeError, load_all, recipes_dir
from ..set_loader import load_all_sets, sets_dir, validate_sets
from ..viewport import frame_selected, hide_startup_cube, prefer_material_preview
from .spawn import (
    clear_lodsmith_objects,
    cursor_origin,
    select_tree,
    spawn_recipe,
    spawn_set,
)


def _format_hits(hits) -> str:
    return " | ".join(f"{hit.kind}:{hit.id} ({hit.score})" for hit in hits[:6])


def _catalog():
    recipes = load_all(recipes_dir())
    sets = load_all_sets(sets_dir())
    validate_sets(sets, recipes)
    return recipes, {recipe.id: recipe for recipe in recipes}, sets


class LODSMITH_OT_plan_prompt(bpy.types.Operator):
    bl_idname = "lodsmith.plan_prompt"
    bl_label = "Plan"
    bl_description = "Rank shipped recipes and sets for the prompt. No network."
    bl_options = {"REGISTER"}

    def execute(self, context):
        prompt = (context.scene.lodsmith_prompt or "").strip()
        if not prompt:
            self.report({"ERROR"}, "Type a prompt (crate, tavern, 선술집)")
            return {"CANCELLED"}
        try:
            recipes, _catalog_map, sets = _catalog()
            hits = plan(prompt, recipes, sets)
        except RecipeError as exc:
            self.report({"ERROR"}, str(exc))
            return {"CANCELLED"}
        if not hits:
            context.scene.lodsmith_last_plan = "no match"
            self.report({"WARNING"}, "No matching recipe or set")
            return {"CANCELLED"}
        context.scene.lodsmith_last_plan = _format_hits(hits)
        top = hits[0]
        self.report({"INFO"}, f"Top: {top.kind} {top.id} ({top.score})")
        return {"FINISHED"}


class LODSMITH_OT_build_prompt(bpy.types.Operator):
    bl_idname = "lodsmith.build_prompt"
    bl_label = "Build prompt"
    bl_description = "Build the best matching recipe or set at the 3D cursor"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        prompt = (context.scene.lodsmith_prompt or "").strip()
        if not prompt:
            self.report({"ERROR"}, "Type a prompt (crate, tavern, 선술집)")
            return {"CANCELLED"}
        try:
            recipes, catalog, sets = _catalog()
            hits = plan(prompt, recipes, sets)
        except RecipeError as exc:
            self.report({"ERROR"}, str(exc))
            return {"CANCELLED"}
        if not hits:
            context.scene.lodsmith_last_plan = "no match"
            self.report({"WARNING"}, "No matching recipe or set")
            return {"CANCELLED"}
        context.scene.lodsmith_last_plan = _format_hits(hits)
        top = hits[0]
        origin = cursor_origin(context)
        if top.kind == "set":
            prop_set = next(item for item in sets if item.id == top.id)
            root, created = spawn_set(context, prop_set, catalog, origin)
            label = f"Built set {prop_set.name} ({len(prop_set.items)} props)"
        else:
            recipe = catalog.get(top.id)
            if recipe is None:
                self.report({"ERROR"}, f"Unknown recipe: {top.id}")
                return {"CANCELLED"}
            root, created = spawn_recipe(
                context,
                recipe,
                root_name=parent_name(recipe.id),
                origin=origin,
                replace=True,
            )
            label = f"Built {recipe.name}"
        select_tree(context, root, created)
        hide_startup_cube(context)
        prefer_material_preview(context)
        frame_selected(context)
        self.report({"INFO"}, label)
        return {"FINISHED"}


class LODSMITH_OT_build_set(bpy.types.Operator):
    bl_idname = "lodsmith.build_set"
    bl_label = "Build set"
    bl_description = "Build the selected set at the 3D cursor"
    bl_options = {"REGISTER", "UNDO"}

    set_id: bpy.props.StringProperty(name="Set", default="tavern")

    def execute(self, context):
        set_id = self.set_id or getattr(context.scene, "lodsmith_set_id", "tavern")
        try:
            recipes, catalog, sets = _catalog()
        except RecipeError as exc:
            self.report({"ERROR"}, str(exc))
            return {"CANCELLED"}
        prop_set = next((item for item in sets if item.id == set_id), None)
        if prop_set is None:
            self.report({"ERROR"}, f"Unknown set: {set_id}")
            return {"CANCELLED"}
        del recipes
        root, created = spawn_set(
            context, prop_set, catalog, cursor_origin(context)
        )
        select_tree(context, root, created)
        hide_startup_cube(context)
        prefer_material_preview(context)
        frame_selected(context)
        self.report(
            {"INFO"},
            f"Built set {prop_set.name} ({len(prop_set.items)} props)",
        )
        return {"FINISHED"}


class LODSMITH_OT_clear(bpy.types.Operator):
    bl_idname = "lodsmith.clear"
    bl_label = "Clear lodsmith"
    bl_description = "Delete lodsmith parents, sets, and parts from the scene"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        del context
        removed = clear_lodsmith_objects()
        self.report({"INFO"}, f"Removed {removed} lodsmith root(s)")
        return {"FINISHED"}
