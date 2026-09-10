"""Word-wrap for the N-panel. Blender labels do not wrap on their own."""

PANEL_HINT = (
    "Ids are claimed once. python -m addon new recipe <id>, then you own the parts. "
    "crate.lid, 72 tris. Don't exec bpy. See CONTRIBUTING.md."
)


def wrap_words(text: str, width: int) -> tuple[str, ...]:
    width = max(8, width)
    lines: list[str] = []
    current = ""
    for word in text.split():
        trial = word if not current else f"{current} {word}"
        if len(trial) <= width:
            current = trial
            continue
        if current:
            lines.append(current)
        current = word
    if current:
        lines.append(current)
    return tuple(lines)


def label_width_chars(region_width: int) -> int:
    return max(16, min(48, region_width // 7 - 2))
