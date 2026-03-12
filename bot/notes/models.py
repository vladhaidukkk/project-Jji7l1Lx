import pickle
from collections import UserDict
from pathlib import Path
from typing import Self

from bot.common import Field
from bot.utils.file_utils import ensure_file_dir_exists


class NoteName(Field):
    def __init__(self, value: str) -> None:
        # Note name validation
        value = value.strip()
        if not value:
            raise ValueError("Note name cannot be empty")

        super().__init__(value)


class NoteContent(Field):
    pass


class NoteTag(Field):
    def __init__(self, value: str) -> None:
        # Note tag validation
        value = value.strip()
        if not value:
            raise ValueError("Tag cannot be empty")

        super().__init__(value)


class Note:
    def __init__(
        self,
        name: str,
        content: str = "",
        tags: list[str] | None = None,
    ) -> None:
        self.name = NoteName(name)
        self.content = NoteContent(content)
        self.tags = [NoteTag(tag) for tag in self.__dedup_tags(tags or [])]

    def preview(self, length: int = 50) -> str:
        preview_text = self.content.value.replace("\n", " ").strip()
        if len(preview_text) > length:
            if length > 3:
                return preview_text[: length - 3] + "..."
            return preview_text[:length]
        return preview_text

    def add_tags(self, tags: list[str]) -> list[str]:
        added_tags: list[str] = []
        existing_tags = {tag.value for tag in self.tags}
        for tag in self.__dedup_tags(tags):
            if tag not in existing_tags:
                self.tags.append(NoteTag(tag))
                added_tags.append(tag)
        return added_tags

    def remove_tags(self, tags: list[str]) -> list[str]:
        removed_tags: list[str] = []
        tags_by_value = {tag.value: tag for tag in self.tags}
        for tag in self.__dedup_tags(tags):
            note_tag = tags_by_value.get(tag)
            if note_tag is not None:
                self.tags.remove(note_tag)
                removed_tags.append(tag)
        return removed_tags

    @staticmethod
    def __dedup_tags(tags: list[str]) -> list[str]:
        seen: set[str] = set()
        unique_tags: list[str] = []
        for tag in tags:
            if tag not in seen:
                seen.add(tag)
                unique_tags.append(tag)
        return unique_tags


class NotesBook(UserDict):
    def add_note(self, note: Note) -> None:
        self.data[note.name.value] = note

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
        path = Path(path)
        ensure_file_dir_exists(path)
        with path.open("wb") as f:
            pickle.dump(self, f)
