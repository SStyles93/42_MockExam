"""Persisted session state, so closing the terminal does not lose the exam."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional


class Session:
    def __init__(self, path: Path, data: dict):
        self.path = path
        self.data = data

    @classmethod
    def load(cls, path: Path) -> Optional["Session"]:
        if not path.is_file():
            return None
        try:
            return cls(path, json.loads(path.read_text(encoding="utf-8")))
        except (OSError, ValueError):
            return None

    @classmethod
    def new(cls, path: Path, **data) -> "Session":
        session = cls(path, data)
        session.save()
        return session

    def save(self) -> None:
        self.path.write_text(json.dumps(self.data, indent=2), encoding="utf-8")

    def clear(self) -> None:
        self.path.unlink(missing_ok=True)

    def __getitem__(self, key):
        return self.data[key]

    def __setitem__(self, key, value):
        self.data[key] = value

    def get(self, key, default=None):
        return self.data.get(key, default)
