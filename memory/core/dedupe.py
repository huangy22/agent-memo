from __future__ import annotations


def has_matching_title(entries: list[dict[str, object]], title: str) -> bool:
    normalized_title = title.strip().lower()
    return any(
        str(entry.get("title", "")).strip().lower() == normalized_title
        for entry in entries
    )


def find_matching_title_index(entries: list[dict[str, object]], title: str) -> int | None:
    normalized_title = title.strip().lower()
    for index, entry in enumerate(entries):
        if str(entry.get("title", "")).strip().lower() == normalized_title:
            return index
    return None
