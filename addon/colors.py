"""Hex color helpers used by the recipe loader (no bpy)."""

from __future__ import annotations

import re

_HEX = re.compile(r"^#[0-9A-Fa-f]{6}$")


def normalize_hex(value: str) -> str:
    return value.strip().lower()


def is_hex_color(value: str) -> bool:
    return bool(_HEX.fullmatch(value.strip()))


def hex_to_rgb(value: str) -> tuple[float, float, float]:
    color = normalize_hex(value)
    return (
        int(color[1:3], 16) / 255.0,
        int(color[3:5], 16) / 255.0,
        int(color[5:7], 16) / 255.0,
    )
