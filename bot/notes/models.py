import pickle
from collections import UserDict
from pathlib import Path
from typing import Self

from bot.common import Field
from bot.utils.file_utils import ensure_file_dir_exists


class NoteName(Field):
    def __init__(self, value: str) -> None:
        """Initialise and validate a note name.

        Args:
            value: The note's name. Leading/trailing whitespace is stripped.

        Raises:
            ValueError: If the stripped value is empty.
        """
        value_stripped = value.strip()
        super().__init__(value_stripped)
        self.value = value_stripped

    @property
    def value(self) -> str:
        """The stored note name string.

        Returns:
            The validated, stripped note name.
        """
        return self._value

    @value.setter
    def value(self, value: str) -> None:
        """Set and validate the note name.

        Args:
            value: New note name string. Stripped before validation.

        Raises:
            ValueError: If the stripped value is empty.
        """
        value_stripped = value.strip()
        if not value_stripped:
            raise ValueError("Note name cannot be empty")
        self._value = value_stripped


class NoteContent(Field):
    @property
    def content(self) -> str:
        """The raw content string.

        Returns:
            The stored content value.
        """
        return self._content

    @content.setter
    def content(self, value: str) -> None:
        """Set the content value.

        Args:
            value: New content string to store.
        """
        self._content = value

    def preview(self, length: int = 50) -> str:
        """Return a truncated, single-line preview of the content.

        Newlines are collapsed to spaces. If the text exceeds *length*
        characters it is truncated and an ellipsis (``...``) is appended.

        Args:
            length: Maximum number of characters in the preview. Defaults to
                ``50``.

        Returns:
            A single-line preview string at most *length* characters long.
        """
        preview_text = self.value.replace("\n", " ").strip()
        if len(preview_text) > length:
            if length > 3:
                return preview_text[: length - 3] + "..."
            return preview_text[:length]
        return preview_text


class NoteTag(Field):
    def __init__(self, value: str) -> None:
        """Initialise and validate a note tag.

        Args:
            value: The tag string. Leading/trailing whitespace is stripped.

        Raises:
            ValueError: If the stripped value is empty.
        """
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
        """Initialise a note with a name, optional content, and optional tags.

        Duplicate tags in *tags* are silently removed.

        Args:
            name: The note's title/name.
            content: The body text of the note. Defaults to an empty string.
            tags: An optional list of tag strings to attach. Duplicates are
                deduplicated automatically.
        """
        self.name = NoteName(name)
        self.content = NoteContent(content)
        self.tags = [NoteTag(tag) for tag in self.__dedup_tags(tags or [])]

    def add_tags(self, tags: list[str]) -> list[str]:
        """Add new tags to the note, ignoring duplicates.

        Args:
            tags: List of tag strings to add. Duplicates within *tags* itself
                and tags already present on the note are both skipped.

        Returns:
            A list of tag strings that were actually added.
        """
        added_tags: list[str] = []
        existing_tags = {tag.value for tag in self.tags}
        for tag in self.__dedup_tags(tags):
            if tag not in existing_tags:
                self.tags.append(NoteTag(tag))
                added_tags.append(tag)
        return added_tags

    def remove_tags(self, tags: list[str]) -> list[str]:
        """Remove tags from the note.

        Tags in *tags* that are not present on the note are silently ignored.

        Args:
            tags: List of tag strings to remove.

        Returns:
            A list of tag strings that were actually removed.
        """
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
        """Return a deduplicated copy of *tags* preserving insertion order.

        Args:
            tags: The list of tag strings to deduplicate.

        Returns:
            A new list with duplicate strings removed while keeping the first
            occurrence of each.
        """
        return list(dict.fromkeys(tags))

    def __str__(self) -> str:
        """Return a concise single-line representation of the note.

        Returns:
            A string in the form ``"<name> [tag1] [tag2]: <content preview>"``.
            The content preview and tag list are omitted when empty.
        """
        tags = " ".join(f"[{tag}]" for tag in self.tags)
        content_preview = self.content.preview(30)
        prefix = f"{self.name} {tags}".strip()
        return f"{prefix}: {content_preview}" if content_preview else prefix


class NotesBook(UserDict):
    def add_note(self, note: Note) -> None:
        """Add a note to the book.

        Args:
            note: The :class:`Note` to store, keyed by its name value.
        """
        self.data[note.name.value] = note

    def find(self, name: str) -> Note | None:
        """Look up a note by name.

        Args:
            name: The note name to search for.

        Returns:
            The :class:`Note` if found, otherwise ``None``.
        """
        return self.data.get(name)

    def delete(self, name: str) -> None:
        """Delete a note by name.

        Args:
            name: The name of the note to remove.

        Raises:
            KeyError: If no note with *name* exists in the book.
        """
        del self.data[name]

    @classmethod
    def from_file(cls, path: str | Path) -> Self:
        """Load a :class:`NotesBook` from a pickle file.

        Args:
            path: Path to the pickle file to read.

        Returns:
            The deserialised :class:`NotesBook`, or a new empty instance if the
            file does not exist.
        """
        try:
            with open(path, "rb") as f:
                return pickle.load(f)
        except FileNotFoundError:
            return cls()

    def save(self, path: str | Path) -> None:
        """Serialise and persist the notes book to a pickle file.

        Args:
            path: Destination file path. Parent directories are created
                automatically if they do not exist.
        """
        path = Path(path)
        ensure_file_dir_exists(path)
        with path.open("wb") as f:
            pickle.dump(self, f)
