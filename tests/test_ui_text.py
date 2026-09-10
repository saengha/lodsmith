from addon.ui_text import PANEL_HINT, label_width_chars, wrap_words


def test_wrap_splits_barrel_description():
    text = "Octagonal stave barrel with floor and lid. Cube staves only."
    lines = wrap_words(text, 22)
    assert len(lines) >= 2
    assert all(len(line) <= 22 or " " not in line for line in lines)
    assert " ".join(lines) == text


def test_label_width_stays_in_range():
    assert label_width_chars(80) == 16
    assert 16 <= label_width_chars(250) <= 48
    assert label_width_chars(800) == 48


def test_panel_hint_points_at_new_recipe():
    assert "new recipe" in PANEL_HINT
    assert "CONTRIBUTING.md" in PANEL_HINT
    assert "72 tris" in PANEL_HINT
    assert "exec bpy" in PANEL_HINT
