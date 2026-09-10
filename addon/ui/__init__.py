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


def register():
    import bpy

    bpy.types.Scene.lodsmith_recipe_id = bpy.props.EnumProperty(
        name="Recipe",
        items=_recipe_items,
    )
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    import bpy

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    if hasattr(bpy.types.Scene, "lodsmith_recipe_id"):
        del bpy.types.Scene.lodsmith_recipe_id
