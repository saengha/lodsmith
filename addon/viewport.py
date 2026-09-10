"""Viewport helpers after Build. Material Preview is allowed; GPU use is fine."""

from __future__ import annotations

import bpy


def hide_startup_cube(context) -> None:
    """Factory files ship a 2m Cube that swallows a 0.8m crate."""
    cube = context.scene.objects.get("Cube")
    if cube is None or cube.parent is not None:
        return
    if cube.name.startswith("lodsmith.") or cube.name.startswith("crate."):
        return
    cube.hide_set(True)


def frame_selected(context) -> None:
    window = getattr(context, "window", None)
    if window is None:
        return
    screen = getattr(window, "screen", None)
    if screen is None:
        return
    for area in screen.areas:
        if area.type != "VIEW_3D":
            continue
        region = next((item for item in area.regions if item.type == "WINDOW"), None)
        if region is None:
            continue
        try:
            with context.temp_override(window=window, area=area, region=region):
                bpy.ops.view3d.view_selected()
        except Exception:
            return
        return


def prefer_material_preview(context) -> None:
    window = getattr(context, "window", None)
    if window is None:
        return
    screen = getattr(window, "screen", None)
    if screen is None:
        return
    for area in screen.areas:
        if area.type != "VIEW_3D":
            continue
        for space in area.spaces:
            if space.type != "VIEW_3D":
                continue
            space.shading.type = "MATERIAL"
