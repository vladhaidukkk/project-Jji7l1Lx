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
        self.__notes = notes

    def create_note(self, name: str, content: str = "") -> None:
        note = self.__notes.find(name)
        if note:
            raise NoteAlreadyExistsError(f"Note '{name}' already exists.")

        note = Note(name, content)
        self.__notes.add_note(note)

    def get_note(self, name: str) -> Note | None:
        return self.__notes.find(name)

    def update_note_content(self, name: str, content: str) -> None:
        note = self.__notes.find(name)
        if not note:
            raise NoteNotFoundError(f"Note '{name}' does not exist.")

        note.content = NoteContent(content)

    def add_or_update_note(
        self,
        name: str,
        content: str,
    ) -> Literal["added", "updated"]:
        note = self.__notes.find(name)
        if not note:
            self.create_note(name, content)
            return "added"

        self.update_note_content(name, content)
        return "updated"

    def add_note_tags(self, name: str, tags: list[str]) -> list[str]:
        note = self.__notes.find(name)
        if not note:
            raise NoteNotFoundError(f"Note '{name}' does not exist.")

        return note.add_tags(tags)

    def remove_note_tags(self, name: str, tags: list[str]) -> list[str]:
        note = self.__notes.find(name)
        if not note:
            raise NoteNotFoundError(f"Note '{name}' does not exist.")

        return note.remove_tags(tags)

    def delete_note(self, name: str) -> None:
        note = self.__notes.find(name)
        if not note:
            raise NoteNotFoundError(f"Note '{name}' does not exist.")

        self.__notes.delete(name)

    def rename_note(
        self,
        old_name: str,
        new_name: str,
    ) -> Literal["renamed", "skipped"]:
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
        note_tag = NoteTag(tag)
        return [
            note
            for note in self.__notes.data.values()
            if any(t.value == note_tag.value for t in note.tags)
        ]

    def list_note_tags(self) -> list[tuple[str, int]]:
        tag_counts = Counter(
            tag.value for note in self.__notes.data.values() for tag in note.tags
        )
        return sorted(tag_counts.items())
