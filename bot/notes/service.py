from typing import Literal

from .errors import NoteAlreadyExistsError, NoteNotFoundError
from .models import Note, NotesBook


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
