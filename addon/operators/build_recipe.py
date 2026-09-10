"""Build the selected recipe into named mesh parts under an empty parent."""

from __future__ import annotations

import bpy

from ..compile import compile_recipe
from ..naming import parent_name
from ..recipe_loader import RecipeError, load_all, recipes_dir
from ..viewport import frame_selected, hide_startup_cube, prefer_material_preview
from .spawn import cursor_origin, select_tree, spawn_recipe


class LODSMITH_OT_build_recipe(bpy.types.Operator):
    bl_idname = "lodsmith.build_recipe"
    bl_label = "Build"
    bl_description = "Create mesh parts from the selected lodsmith recipe"
    bl_options = {"REGISTER", "UNDO"}

    recipe_id: bpy.props.StringProperty(name="Recipe", default="crate")

    def execute(self, context):
        recipe_id = self.recipe_id or getattr(
            context.scene, "lodsmith_recipe_id", "crate"
        )
        try:
            recipes = {recipe.id: recipe for recipe in load_all(recipes_dir())}
        except RecipeError as exc:
            self.report({"ERROR"}, str(exc))
            return {"CANCELLED"}

        recipe = recipes.get(recipe_id)
        if recipe is None:
            self.report({"ERROR"}, f"Unknown recipe: {recipe_id}")
            return {"CANCELLED"}

        compiled = compile_recipe(recipe)
        root, created = spawn_recipe(
            context,
            recipe,
            root_name=parent_name(recipe.id),
            origin=cursor_origin(context),
            replace=True,
        )
        select_tree(context, root, created)
        hide_startup_cube(context)
        prefer_material_preview(context)
        frame_selected(context)
        self.report(
            {"INFO"},
            f"Built {recipe.name} ({len(recipe.parts)} parts, "
            f"target {compiled.target_tris} tris)",
        )
        return {"FINISHED"}
