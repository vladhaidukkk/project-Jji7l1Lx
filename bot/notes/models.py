import pickle
from collections import UserDict
from pathlib import Path
from typing import Self

from bot.common import Field
from bot.utils.file_utils import ensure_file_dir_exists


class NoteName(Field):
    def __init__(self, value: str) -> None:
        value_stripped = value.strip()
        super().__init__(value_stripped)
        self.value = value_stripped

    @property
    def value(self) -> str:
        return self._value

    @value.setter
    def value(self, value: str) -> None:
        value_stripped = value.strip()
        if not value_stripped:
            raise ValueError("Note name cannot be empty")
        self._value = value_stripped


class NoteContent(Field):
    @property
    def content(self) -> str:
        return self._content

    @content.setter
    def content(self, value: str) -> None:
        self._content = value

    def preview(self, length: int = 50) -> str:
        preview_text = self.value.replace("\n", " ").strip()
        if len(preview_text) > length:
            if length > 3:
                return preview_text[: length - 3] + "..."
            return preview_text[:length]
        return preview_text


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
        return list(dict.fromkeys(tags))

    def __str__(self) -> str:
        tags = " ".join(f"[{tag}]" for tag in self.tags)
        content_preview = self.content.preview(30)
        prefix = f"{self.name} {tags}".strip()
        return f"{prefix}: {content_preview}" if content_preview else prefix


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
