import bpy


class LODSMITH_PT_sidebar(bpy.types.Panel):
    bl_label = "Lodsmith"
    bl_idname = "LODSMITH_PT_sidebar"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Lodsmith"

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.prop(scene, "lodsmith_recipe_id", text="Recipe")
        op = layout.operator("lodsmith.build_recipe", text="Build")
        op.recipe_id = scene.lodsmith_recipe_id
