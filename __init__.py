"""Blender 4.2+ extension entry. Register lives in the addon package."""

from . import addon


def register():
    addon.register()


def unregister():
    addon.unregister()
