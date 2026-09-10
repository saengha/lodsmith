import bpy

from ..recipe_loader import RecipeError, load_all, recipes_dir
from ..set_loader import load_all_sets, sets_dir
from ..ui_text import PANEL_HINT, label_width_chars, wrap_words


class LODSMITH_PT_sidebar(bpy.types.Panel):
    bl_label = "Lodsmith"
    bl_idname = "LODSMITH_PT_sidebar"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Lodsmith"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        width = label_width_chars(context.region.width)

        layout.prop(scene, "lodsmith_prompt", text="Prompt")
        row = layout.row(align=True)
        row.operator("lodsmith.plan_prompt", text="Plan")
        row.operator("lodsmith.build_prompt", text="Build prompt")
        plan = (scene.lodsmith_last_plan or "").strip()
        if plan:
            for line in wrap_words(plan, width):
                layout.label(text=line)

        layout.separator()
        layout.prop(scene, "lodsmith_set_id", text="Set")
        prop_set = _selected_set(scene.lodsmith_set_id)
        if prop_set is not None:
            layout.label(text=f"{len(prop_set.items)} props")
            for line in wrap_words(prop_set.description, width):
                layout.label(text=line)
        set_op = layout.operator("lodsmith.build_set", text="Build set")
        set_op.set_id = scene.lodsmith_set_id

        layout.separator()
        layout.prop(scene, "lodsmith_recipe_id", text="Recipe")
        recipe = _selected_recipe(scene.lodsmith_recipe_id)
        if recipe is not None:
            layout.label(text=f"{len(recipe.parts)} parts · {recipe.target_tris} tris")
            for line in wrap_words(recipe.description, width):
                layout.label(text=line)
        op = layout.operator("lodsmith.build_recipe", text="Build")
        op.recipe_id = scene.lodsmith_recipe_id
        layout.prop(scene, "lodsmith_on_ground", text="Snap Z to ground")
        layout.operator("lodsmith.validate_prop", text="Validate")
        layout.operator("lodsmith.export_glb", text="Export GLB")
        layout.operator("lodsmith.clear", text="Clear lodsmith")
        layout.separator()
        for line in wrap_words(PANEL_HINT, width):
            layout.label(text=line)


def _selected_recipe(recipe_id: str):
    try:
        recipes = {recipe.id: recipe for recipe in load_all(recipes_dir())}
    except RecipeError:
        return None
    return recipes.get(recipe_id)


def _selected_set(set_id: str):
    try:
        catalog = {item.id: item for item in load_all_sets(sets_dir())}
    except RecipeError:
        return None
    return catalog.get(set_id)
