"""Build the selected recipe into named mesh parts under an empty parent."""

from __future__ import annotations

import bpy

from ..recipe_loader import RecipeError, load_all, recipes_dir


class LODSMITH_OT_build_recipe(bpy.types.Operator):
    bl_idname = "lodsmith.build_recipe"
    bl_label = "Build"
    bl_description = "Create mesh parts from the selected lodsmith recipe"
    bl_options = {"REGISTER", "UNDO"}

    recipe_id: bpy.props.StringProperty(name="Recipe", default="crate")

    def execute(self, context):
        recipe_id = self.recipe_id or getattr(context.scene, "lodsmith_recipe_id", "crate")
        try:
            recipes = {recipe.id: recipe for recipe in load_all(recipes_dir())}
        except RecipeError as exc:
            self.report({"ERROR"}, str(exc))
            return {"CANCELLED"}

        recipe = recipes.get(recipe_id)
        if recipe is None:
            self.report({"ERROR"}, f"Unknown recipe: {recipe_id}")
            return {"CANCELLED"}

        parent = bpy.data.objects.new(f"lodsmith.{recipe.id}", None)
        context.collection.objects.link(parent)

        created = []
        for part in recipe.parts:
            bpy.ops.mesh.primitive_cube_add(size=1.0, location=part.location)
            obj = context.active_object
            obj.name = f"{recipe.id}.{part.name}"
            obj.scale = part.size
            obj.parent = parent
            created.append(obj)

        for obj in created:
            obj.select_set(True)
        parent.select_set(True)
        context.view_layer.objects.active = parent
        self.report(
            {"INFO"},
            f"Built {recipe.name} ({len(recipe.parts)} parts, target {recipe.target_tris} tris)",
        )
        return {"FINISHED"}
