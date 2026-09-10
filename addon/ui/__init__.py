from .panel import LODSMITH_PT_sidebar

classes = (LODSMITH_PT_sidebar,)


def _recipe_items(self, context):
    del self, context
    from ..recipe_loader import RecipeError, load_all, recipes_dir

    try:
        recipes = load_all(recipes_dir())
    except RecipeError:
        return [("crate", "Crate", "Could not load recipes; default id")]
    if not recipes:
        return [("crate", "Crate", "No JSON recipes found")]
    return [(recipe.id, recipe.name, recipe.description or recipe.id) for recipe in recipes]


def _set_items(self, context):
    del self, context
    from ..recipe_loader import RecipeError
    from ..set_loader import load_all_sets, sets_dir

    try:
        catalog = load_all_sets(sets_dir())
    except RecipeError:
        return [("tavern", "Tavern", "Could not load sets; default id")]
    if not catalog:
        return [("tavern", "Tavern", "No JSON sets found")]
    return [(item.id, item.name, item.description or item.id) for item in catalog]


def register():
    import bpy

    bpy.types.Scene.lodsmith_recipe_id = bpy.props.EnumProperty(
        name="Recipe",
        items=_recipe_items,
    )
    bpy.types.Scene.lodsmith_set_id = bpy.props.EnumProperty(
        name="Set",
        items=_set_items,
    )
    bpy.types.Scene.lodsmith_prompt = bpy.props.StringProperty(
        name="Prompt",
        description="Local keyword plan: crate, tavern, warehouse, 선술집",
        default="",
    )
    bpy.types.Scene.lodsmith_last_plan = bpy.props.StringProperty(
        name="Last plan",
        default="",
    )
    bpy.types.Scene.lodsmith_on_ground = bpy.props.BoolProperty(
        name="Snap Z to ground",
        description="Use the 3D cursor XY and keep Z at 0",
        default=True,
    )
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    import bpy

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    for attr in (
        "lodsmith_recipe_id",
        "lodsmith_set_id",
        "lodsmith_prompt",
        "lodsmith_last_plan",
        "lodsmith_on_ground",
    ):
        if hasattr(bpy.types.Scene, attr):
            delattr(bpy.types.Scene, attr)
