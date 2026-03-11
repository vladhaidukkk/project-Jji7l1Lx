from typing import Any, Literal

from rapidfuzz import fuzz

from .errors import NoteAlreadyExistsError, NoteNotFoundError
from .models import Note, NotesBook

SearchResultItem = tuple[Note, float, Any, Any]


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

        note.content = content

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
    ) -> list[SearchResultItem]:
        query = query.lower()

        matches: list[SearchResultItem] = []
        for note in self.__notes.data.values():
            # Match against name (case-insensitive)
            name_res = fuzz.partial_ratio_alignment(query, note.name.lower())
            name_score = name_res.score if name_res else 0.0

            # Match against content (case-insensitive)
            content_res = fuzz.partial_ratio_alignment(query, note.content.lower())
            content_score = content_res.score if content_res else 0.0

            # Keep the best match for this note
            best_score = max(name_score, content_score)
            if best_score >= score_cutoff:
                matches.append((note, best_score, name_res, content_res))

        # Sort matches by highest score
        matches.sort(key=lambda x: x[1], reverse=True)
        return matches[:limit]
