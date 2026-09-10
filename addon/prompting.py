"""Expand a user prompt into English planner tokens. No network."""

from __future__ import annotations

# Longer keys first so "보물상자" wins over "상자" and "창문" wins over "문".
KO_ALIASES: tuple[tuple[str, str], ...] = (
    ("보물상자", "chest loot"),
    ("상자더미", "crate stack"),
    ("선술집", "tavern"),
    ("술집", "tavern"),
    ("대장간", "smithy forge"),
    ("여관", "inn lodging"),
    ("창고", "warehouse"),
    ("야영지", "camp"),
    ("캠프", "camp"),
    ("모닥불", "firepit campfire"),
    ("가마솥", "cauldron stew"),
    ("마당", "yard"),
    ("울타리", "fence"),
    ("표지판", "signpost"),
    ("랜턴", "lantern"),
    ("등불", "lantern"),
    ("팔레트", "pallet"),
    ("테이블", "table"),
    ("탁자", "table"),
    ("스툴", "stool"),
    ("걸상", "stool"),
    ("의자", "chair"),
    ("침대", "bed mattress"),
    ("벤치", "bench"),
    ("술통", "barrel"),
    ("배럴", "barrel"),
    ("케그", "keg barrel"),
    ("상자", "crate"),
    ("박스", "crate"),
    ("궤짝", "chest"),
    ("모루", "anvil horn"),
    ("망치", "hammer peen"),
    ("텐트", "tent canvas"),
    ("초", "candle"),
    ("양초", "candle"),
    ("잔", "mug"),
    ("머그", "mug"),
    ("병", "bottle cork"),
    ("책", "book tome"),
    ("자루", "sack"),
    ("선반", "shelf"),
    ("시장", "market"),
    ("노점", "market stall"),
    ("출입구", "entrance"),
    ("창문", "window"),
    ("창틀", "window"),
    ("사다리", "ladder"),
    ("수레", "cart"),
    ("마차", "cart"),
    ("카트", "cart"),
    ("우물가", "wellside"),
    ("우물", "well"),
    ("파사드", "facade"),
    ("외벽", "facade"),
    ("문", "door"),
    ("횃불", "torch"),
    ("양동이", "bucket"),
    ("물통", "bucket"),
)


def expand_prompt(prompt: str) -> str:
    text = prompt.strip()
    lowered = text.casefold()
    extras: list[str] = []
    matched: list[str] = []
    for korean, english in sorted(KO_ALIASES, key=lambda item: -len(item[0])):
        if korean not in text and korean not in lowered:
            continue
        remaining = text
        remaining_lower = lowered
        for longer in matched:
            remaining = remaining.replace(longer, " ")
            remaining_lower = remaining_lower.replace(longer, " ")
        if korean not in remaining and korean not in remaining_lower:
            continue
        extras.append(english)
        matched.append(korean)
    if extras:
        return f"{text} {' '.join(extras)}"
    return text
