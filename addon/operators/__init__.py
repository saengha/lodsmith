from .build_recipe import LODSMITH_OT_build_recipe

classes = (LODSMITH_OT_build_recipe,)


def register():
    import bpy

    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    import bpy

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
