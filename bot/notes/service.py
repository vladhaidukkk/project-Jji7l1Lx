from collections import Counter
from typing import Literal, NamedTuple, Optional

from bot.utils.search_utils import fuzzy_search, sort_and_limit_matches
from rapidfuzz.distance import ScoreAlignment

from .errors import NoteAlreadyExistsError, NoteNotFoundError
from .models import Note, NoteContent, NoteName, NotesBook, NoteTag


class SearchResultItemForNotes(NamedTuple):
    note: Note
    best_score: float
    name_alignment: Optional[ScoreAlignment]
    content_alignment: Optional[ScoreAlignment]

class NotesService:
    def __init__(self, notes: NotesBook) -> None:
        """Initialise the service with a notes book.

        Args:
            notes: The :class:`NotesBook` instance this service operates on.
        """
        self.__notes = notes

    def create_note(self, name: str, content: str = "") -> None:
        """Create a new note.

        Args:
            name: The title/name for the new note.
            content: Optional initial body text. Defaults to an empty string.

        Raises:
            NoteAlreadyExistsError: If a note named *name* already exists.
        """
        note = self.__notes.find(name)
        if note:
            raise NoteAlreadyExistsError(f"Note '{name}' already exists.")

        note = Note(name, content)
        self.__notes.add_note(note)

    def get_note(self, name: str) -> Note | None:
        """Retrieve a note by name.

        Args:
            name: The note name to look up.

        Returns:
            The :class:`Note` if found, otherwise ``None``.
        """
        return self.__notes.find(name)

    def update_note_content(self, name: str, content: str) -> None:
        """Replace the body text of an existing note.

        Args:
            name: The note's name.
            content: The new body text.

        Raises:
            NoteNotFoundError: If no note named *name* exists.
        """
        note = self.__notes.find(name)
        if not note:
            raise NoteNotFoundError(f"Note '{name}' does not exist.")

        note.content = NoteContent(content)

    def add_or_update_note(
        self,
        name: str,
        content: str,
    ) -> Literal["added", "updated"]:
        """Create a note or update its content if it already exists.

        Args:
            name: The note's name.
            content: The body text to set.

        Returns:
            ``"added"`` if a new note was created, or ``"updated"`` if an
            existing note's content was replaced.
        """
        note = self.__notes.find(name)
        if not note:
            self.create_note(name, content)
            return "added"

        self.update_note_content(name, content)
        return "updated"

    def add_note_tags(self, name: str, tags: list[str]) -> list[str]:
        """Add tags to an existing note.

        Args:
            name: The note's name.
            tags: List of tag strings to add.

        Returns:
            A list of tag strings that were actually added (duplicates skipped).

        Raises:
            NoteNotFoundError: If no note named *name* exists.
        """
        note = self.__notes.find(name)
        if not note:
            raise NoteNotFoundError(f"Note '{name}' does not exist.")

        return note.add_tags(tags)

    def remove_note_tags(self, name: str, tags: list[str]) -> list[str]:
        """Remove tags from an existing note.

        Args:
            name: The note's name.
            tags: List of tag strings to remove.

        Returns:
            A list of tag strings that were actually removed.

        Raises:
            NoteNotFoundError: If no note named *name* exists.
        """
        note = self.__notes.find(name)
        if not note:
            raise NoteNotFoundError(f"Note '{name}' does not exist.")

        return note.remove_tags(tags)

    def delete_note(self, name: str) -> None:
        """Permanently delete a note.

        Args:
            name: The name of the note to delete.

        Raises:
            NoteNotFoundError: If no note named *name* exists.
        """
        note = self.__notes.find(name)
        if not note:
            raise NoteNotFoundError(f"Note '{name}' does not exist.")

        self.__notes.delete(name)

    def rename_note(
        self,
        old_name: str,
        new_name: str,
    ) -> Literal["renamed", "skipped"]:
        """Rename a note.

        Args:
            old_name: The current name of the note.
            new_name: The desired new name.

        Returns:
            ``"renamed"`` if the note was renamed, or ``"skipped"`` if
            *old_name* and *new_name* are identical.

        Raises:
            NoteNotFoundError: If no note named *old_name* exists.
            NoteAlreadyExistsError: If a note named *new_name* already exists.
        """
        if old_name == new_name:
            return "skipped"

        note = self.__notes.find(old_name)
        if not note:
            raise NoteNotFoundError(f"Note '{old_name}' does not exist.")

        if self.__notes.find(new_name):
            raise NoteAlreadyExistsError(f"Note '{new_name}' already exists.")

        new_name = NoteName(new_name)
        self.__notes.delete(old_name)
        note.name = new_name
        self.__notes.add_note(note)
        return "renamed"

    def search_notes(
        self,
        query: str,
        *,
        score_cutoff: float = 50.0,
        limit: int = 5,
    ) -> list[SearchResultItemForNotes]:
        """Search notes by title and content using fuzzy matching.

        Args:
            query: The search string (case-insensitive).
            score_cutoff: Minimum fuzzy-match score (0–100) for a note to be
                included. Defaults to ``50.0``.
            limit: Maximum number of results to return. Defaults to ``5``.

        Returns:
            A list of :class:`SearchResultItemForNotes` tuples sorted by
            descending best score, capped at *limit* entries.
        """
        query = query.lower()

        matches: list[SearchResultItemForNotes] = []

        for note in self.__notes.data.values():
            # Match against name (case-insensitive)
            name_score, name_res = fuzzy_search(query, note.name.value.lower())

            # Match against content (case-insensitive)
            content_score, content_res = fuzzy_search(query, note.content.value.lower())

            # Keep the best match for this note
            best_score = max(name_score, content_score)
            if best_score >= score_cutoff:
                matches.append(SearchResultItemForNotes(note, best_score, name_res, content_res))

        # Sort and limit matches by highest score
        return sort_and_limit_matches(matches, limit, sort_key=lambda item: item.best_score)

    def search_notes_by_tag(self, tag: str) -> list[Note]:
        """Return all notes that carry the given tag.

        Args:
            tag: The tag string to filter by (exact match after stripping).

        Returns:
            A list of :class:`Note` objects that have *tag* attached.
        """
        note_tag = NoteTag(tag)
        return [
            note
            for note in self.__notes.data.values()
            if any(t.value == note_tag.value for t in note.tags)
        ]

    def list_note_tags(self) -> list[tuple[str, int]]:
        """Return all tags used across notes together with their usage counts.

        Returns:
            A list of ``(tag, count)`` tuples sorted alphabetically by tag name.
        """
        tag_counts = Counter(
            tag.value for note in self.__notes.data.values() for tag in note.tags
        )
        return sorted(tag_counts.items())
