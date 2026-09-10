"""Create cube meshes without bpy.ops (works in background, no GPU path)."""

from __future__ import annotations

import bpy

from ..geometry import UNIT_CUBE_FACES, cube_vertices_local


def new_cube_object(
    collection,
    name: str,
    size: tuple[float, float, float],
    location: tuple[float, float, float],
    rotation_deg: tuple[float, float, float],
):
    mesh = bpy.data.meshes.new(name)
    mesh.from_pydata(cube_vertices_local(size, rotation_deg), [], UNIT_CUBE_FACES)
    mesh.validate()
    mesh.update()
    for polygon in mesh.polygons:
        polygon.use_smooth = False
    obj = bpy.data.objects.new(name, mesh)
    collection.objects.link(obj)
    obj.location = location
    return obj
