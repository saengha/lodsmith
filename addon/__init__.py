"""Lodsmith Blender add-on: recipe list + Build operator."""


def register():
    from . import operators, ui

    operators.register()
    ui.register()


def unregister():
    from . import operators, ui

    ui.unregister()
    operators.unregister()
