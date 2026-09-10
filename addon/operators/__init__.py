from .build_prompt import (
    LODSMITH_OT_build_prompt,
    LODSMITH_OT_build_set,
    LODSMITH_OT_clear,
    LODSMITH_OT_plan_prompt,
)
from .build_recipe import LODSMITH_OT_build_recipe
from .export_glb import LODSMITH_OT_export_glb
from .validate_prop import LODSMITH_OT_validate_prop

classes = (
    LODSMITH_OT_build_recipe,
    LODSMITH_OT_plan_prompt,
    LODSMITH_OT_build_prompt,
    LODSMITH_OT_build_set,
    LODSMITH_OT_clear,
    LODSMITH_OT_export_glb,
    LODSMITH_OT_validate_prop,
)


def register():
    import bpy

    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    import bpy

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
