import pickle
import pytest
from pathlib import Path

from bot.notes.models import Note, NoteContent, NoteName, NotesBook, NoteTag

pytestmark = [pytest.mark.notes, pytest.mark.models]


# ---------------------------------------------------------------------------
# NoteName
# ---------------------------------------------------------------------------

class TestNoteName:
    def test_valid_name(self):
        n = NoteName("My Note")
        assert n.value == "My Note"

    def test_strips_whitespace(self):
        n = NoteName("  hello  ")
        assert n.value == "hello"

    def test_empty_raises(self):
        with pytest.raises(ValueError):
            NoteName("")

    def test_whitespace_only_raises(self):
        with pytest.raises(ValueError):
            NoteName("   ")

    def test_str(self):
        n = NoteName("Title")
        assert str(n) == "Title"

    def test_setter_strips_and_validates(self):
        n = NoteName("original")
        n.value = "  updated  "
        assert n.value == "updated"

    def test_setter_empty_raises(self):
        n = NoteName("original")
        with pytest.raises(ValueError):
            n.value = ""


# ---------------------------------------------------------------------------
# NoteContent
# ---------------------------------------------------------------------------

class TestNoteContent:
    def test_stores_value(self):
        c = NoteContent("Hello world")
        assert c.value == "Hello world"

    def test_preview_short_text(self):
        c = NoteContent("Short")
        assert c.preview() == "Short"

    def test_preview_truncates_long_text(self):
        c = NoteContent("A" * 60)
        result = c.preview(50)
        assert len(result) == 50
        assert result.endswith("...")

    def test_preview_collapses_newlines(self):
        c = NoteContent("line1\nline2\nline3")
        assert "\n" not in c.preview()

    def test_preview_exact_length(self):
        c = NoteContent("A" * 50)
        result = c.preview(50)
        assert result == "A" * 50

    def test_preview_length_3_no_ellipsis(self):
        c = NoteContent("ABCDE")
        result = c.preview(3)
        assert len(result) == 3

    def test_empty_content(self):
        c = NoteContent("")
        assert c.value == ""
        assert c.preview() == ""


# ---------------------------------------------------------------------------
# NoteTag
# ---------------------------------------------------------------------------

class TestNoteTag:
    def test_valid_tag(self):
        t = NoteTag("python")
        assert t.value == "python"

    def test_strips_whitespace(self):
        t = NoteTag("  work  ")
        assert t.value == "work"

    def test_empty_raises(self):
        with pytest.raises(ValueError):
            NoteTag("")

    def test_whitespace_only_raises(self):
        with pytest.raises(ValueError):
            NoteTag("   ")

    def test_str(self):
        t = NoteTag("urgent")
        assert str(t) == "urgent"


# ---------------------------------------------------------------------------
# Note
# ---------------------------------------------------------------------------

class TestNote:
    def test_init_defaults(self):
        note = Note("My Note")
        assert note.name.value == "My Note"
        assert note.content.value == ""
        assert note.tags == []

    def test_init_with_content_and_tags(self):
        note = Note("Title", "Body text", ["tag1", "tag2"])
        assert note.content.value == "Body text"
        assert len(note.tags) == 2
        assert note.tags[0].value == "tag1"

    def test_init_deduplicates_tags(self):
        note = Note("Title", tags=["a", "b", "a"])
        assert len(note.tags) == 2

    def test_add_tags_new(self):
        note = Note("Note")
        added = note.add_tags(["x", "y"])
        assert added == ["x", "y"]
        assert len(note.tags) == 2

    def test_add_tags_skips_existing(self):
        note = Note("Note", tags=["x"])
        added = note.add_tags(["x", "y"])
        assert added == ["y"]
        assert len(note.tags) == 2

    def test_add_tags_deduplicates_input(self):
        note = Note("Note")
        added = note.add_tags(["a", "a"])
        assert added == ["a"]
        assert len(note.tags) == 1

    def test_remove_tags_existing(self):
        note = Note("Note", tags=["a", "b", "c"])
        removed = note.remove_tags(["a", "c"])
        assert removed == ["a", "c"]
        assert len(note.tags) == 1
        assert note.tags[0].value == "b"

    def test_remove_tags_ignores_missing(self):
        note = Note("Note", tags=["a"])
        removed = note.remove_tags(["z"])
        assert removed == []
        assert len(note.tags) == 1

    def test_str_with_content_and_tags(self):
        note = Note("Title", "Some content", ["tag1"])
        result = str(note)
        assert "Title" in result
        assert "tag1" in result
        assert "Some content" in result

    def test_str_no_content(self):
        note = Note("Title")
        result = str(note)
        assert ":" not in result

    def test_str_no_tags(self):
        note = Note("Title", "Content")
        result = str(note)
        assert "[" not in result


# ---------------------------------------------------------------------------
# NotesBook
# ---------------------------------------------------------------------------

class TestNotesBook:
    def test_add_and_find(self):
        book = NotesBook()
        note = Note("Test")
        book.add_note(note)
        assert book.find("Test") is note

    def test_find_missing_returns_none(self):
        book = NotesBook()
        assert book.find("nonexistent") is None

    def test_delete_existing(self):
        book = NotesBook()
        book.add_note(Note("ToDelete"))
        book.delete("ToDelete")
        assert book.find("ToDelete") is None

    def test_delete_missing_raises(self):
        book = NotesBook()
        with pytest.raises(KeyError):
            book.delete("ghost")

    def test_from_file_missing_file_returns_empty(self, tmp_path):
        book = NotesBook.from_file(tmp_path / "nonexistent.pkl")
        assert isinstance(book, NotesBook)
        assert len(book.data) == 0

    def test_save_and_load_roundtrip(self, tmp_path):
        path = tmp_path / "notes.pkl"
        book = NotesBook()
        book.add_note(Note("Saved Note", "content", ["tag1"]))
        book.save(path)

        loaded = NotesBook.from_file(path)
        note = loaded.find("Saved Note")
        assert note is not None
        assert note.content.value == "content"
        assert note.tags[0].value == "tag1"

