from addon.prompting import expand_prompt


def test_expand_keeps_english():
    assert expand_prompt("wooden keg") == "wooden keg"


def test_expand_korean_tavern():
    text = expand_prompt("선술집 하나")
    assert "tavern" in text


def test_expand_korean_crate_not_just_box_substring():
    text = expand_prompt("보물상자")
    assert "chest" in text
    assert "loot" in text
    assert "crate" not in text


def test_expand_korean_window_does_not_also_mean_door():
    text = expand_prompt("창문")
    assert "window" in text
    assert "door" not in text


def test_expand_korean_wellside_not_just_well():
    text = expand_prompt("우물가")
    assert "wellside" in text
    assert expand_prompt("우물").endswith("well")


def test_expand_korean_chair_not_stool():
    text = expand_prompt("의자")
    assert "chair" in text
    assert "stool" not in text
    assert "stool" in expand_prompt("스툴")


def test_expand_korean_anvil_and_firepit():
    assert "anvil" in expand_prompt("모루")
    assert "firepit" in expand_prompt("모닥불")
    assert "smithy" in expand_prompt("대장간")
    assert "inn" in expand_prompt("여관")
