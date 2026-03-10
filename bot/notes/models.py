import pickle
from collections import UserDict
from pathlib import Path
from typing import Self


class Note:
    def __init__(self, name: str, content: str = "") -> None:
        if not name:
            raise ValueError("Note name cannot be empty")

        self.name = name
        self.content = content

    def preview(self, length: int = 50) -> str:
        preview_text = self.content.replace("\n", " ").strip()
        if len(preview_text) > length:
            return preview_text[: length - 3] + "..."
        return preview_text


class NotesBook(UserDict):
    def add_note(self, note: Note) -> None:
        self.data[note.name] = note

    def find(self, name: str) -> Note | None:
        return self.data.get(name)

    def delete(self, name: str) -> None:
        del self.data[name]

    @classmethod
    def from_file(cls, path: str | Path) -> Self:
        try:
            with open(path, "rb") as f:
                return pickle.load(f)
        except FileNotFoundError:
            return cls()

    def save(self, path: str | Path) -> None:
        with open(path, "wb") as f:
            pickle.dump(self, f)
