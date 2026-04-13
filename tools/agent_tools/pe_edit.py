"""Shared helpers for editing pokeemerald source files.

These files contain non-UTF-8 bytes (game-text special chars), so we work in
latin-1 to round-trip safely.
"""
from pathlib import Path


def read(path: Path) -> str:
    return path.read_bytes().decode("latin-1")


def write(path: Path, text: str) -> None:
    path.write_bytes(text.encode("latin-1"))


def insert_before(text: str, anchor: str, payload: str) -> str:
    """Insert `payload` immediately before the first occurrence of `anchor`."""
    idx = text.index(anchor)
    return text[:idx] + payload + text[idx:]


def insert_after(text: str, anchor: str, payload: str) -> str:
    idx = text.index(anchor) + len(anchor)
    return text[:idx] + payload + text[idx:]


def replace_once(text: str, old: str, new: str) -> str:
    if old not in text:
        raise ValueError(f"Anchor not found: {old[:80]!r}")
    if text.count(old) > 1:
        raise ValueError(f"Anchor not unique: {old[:80]!r}")
    return text.replace(old, new, 1)
