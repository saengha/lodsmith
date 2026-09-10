"""Export the active lodsmith parent (or selection) to GLB."""

from __future__ import annotations

from pathlib import Path

import bpy


class LODSMITH_OT_export_glb(bpy.types.Operator):
    bl_idname = "lodsmith.export_glb"
    bl_label = "Export GLB"
    bl_description = "Export the active object and its children as a GLB"
    bl_options = {"REGISTER"}

    filepath: bpy.props.StringProperty(subtype="FILE_PATH")
    filename_ext = ".glb"
    filter_glob: bpy.props.StringProperty(default="*.glb", options={"HIDDEN"})

    def invoke(self, context, event):
        del event
        active = context.view_layer.objects.active
        suggested = "prop.glb"
        if active is not None:
            suggested = f"{active.name}.glb".replace(" ", "_")
        self.filepath = str(Path.home() / suggested)
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}

    def execute(self, context):
        active = context.view_layer.objects.active
        if active is None:
            self.report({"ERROR"}, "Select a lodsmith parent (or any object) first")
            return {"CANCELLED"}

        for obj in context.view_layer.objects:
            obj.select_set(False)
        active.select_set(True)
        for child in active.children_recursive:
            child.select_set(True)
        context.view_layer.objects.active = active

        path = self.filepath or str(Path.home() / f"{active.name}.glb")
        if not path.lower().endswith(".glb"):
            path = path + ".glb"

        bpy.ops.export_scene.gltf(**_gltf_kwargs(path))
        self.report({"INFO"}, f"Exported {path}")
        return {"FINISHED"}


def _gltf_kwargs(path: str) -> dict:
    kwargs = {
        "filepath": path,
        "export_format": "GLB",
        "use_selection": True,
        "export_apply": True,
    }
    identifiers = {
        prop.identifier for prop in bpy.ops.export_scene.gltf.get_rna_type().properties
    }
    if "export_draco_mesh_compression_enable" in identifiers:
        kwargs["export_draco_mesh_compression_enable"] = False
    if "export_gpu_instances" in identifiers:
        kwargs["export_gpu_instances"] = False
    return kwargs
