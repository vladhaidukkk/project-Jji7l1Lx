import pytest

from bot.notes.errors import NoteAlreadyExistsError, NoteNotFoundError
from bot.notes.models import Note, NotesBook
from bot.notes.service import NotesService

pytestmark = [pytest.mark.notes, pytest.mark.service]


# ---------------------------------------------------------------------------
# Helpers / fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def book() -> NotesBook:
    return NotesBook()


@pytest.fixture
def service(book: NotesBook) -> NotesService:
    return NotesService(book)


@pytest.fixture
def populated_service(service: NotesService) -> NotesService:
    """Service pre-loaded with a few notes."""
    service.create_note("Alpha", "content about alpha")
    service.create_note("Beta", "content about beta")
    service.create_note("Gamma", "completely different stuff")
    return service


# ---------------------------------------------------------------------------
# create_note
# ---------------------------------------------------------------------------

class TestCreateNote:
    def test_creates_note(self, service):
        service.create_note("MyNote", "body")
        assert service.get_note("MyNote") is not None

    def test_created_note_has_content(self, service):
        service.create_note("MyNote", "body text")
        assert service.get_note("MyNote").content.value == "body text"

    def test_default_empty_content(self, service):
        service.create_note("EmptyNote")
        assert service.get_note("EmptyNote").content.value == ""

    def test_duplicate_raises(self, service):
        service.create_note("Dup")
        with pytest.raises(NoteAlreadyExistsError):
            service.create_note("Dup")


# ---------------------------------------------------------------------------
# get_note
# ---------------------------------------------------------------------------

class TestGetNote:
    def test_returns_note(self, service):
        service.create_note("Note1")
        note = service.get_note("Note1")
        assert note is not None
        assert note.name.value == "Note1"

    def test_returns_none_for_missing(self, service):
        assert service.get_note("Ghost") is None


# ---------------------------------------------------------------------------
# update_note_content
# ---------------------------------------------------------------------------

class TestUpdateNoteContent:
    def test_updates_content(self, service):
        service.create_note("N", "old")
        service.update_note_content("N", "new")
        assert service.get_note("N").content.value == "new"

    def test_missing_note_raises(self, service):
        with pytest.raises(NoteNotFoundError):
            service.update_note_content("Ghost", "anything")


# ---------------------------------------------------------------------------
# add_or_update_note
# ---------------------------------------------------------------------------

class TestAddOrUpdateNote:
    def test_add_new_returns_added(self, service):
        result = service.add_or_update_note("New", "body")
        assert result == "added"
        assert service.get_note("New") is not None

    def test_update_existing_returns_updated(self, service):
        service.create_note("Existing", "old")
        result = service.add_or_update_note("Existing", "new")
        assert result == "updated"
        assert service.get_note("Existing").content.value == "new"


# ---------------------------------------------------------------------------
# add_note_tags
# ---------------------------------------------------------------------------

class TestAddNoteTags:
    def test_adds_tags(self, service):
        service.create_note("N")
        added = service.add_note_tags("N", ["a", "b"])
        assert added == ["a", "b"]
        assert len(service.get_note("N").tags) == 2

    def test_skips_duplicate_tags(self, service):
        service.create_note("N")
        service.add_note_tags("N", ["a"])
        added = service.add_note_tags("N", ["a", "b"])
        assert added == ["b"]

    def test_missing_note_raises(self, service):
        with pytest.raises(NoteNotFoundError):
            service.add_note_tags("Ghost", ["tag"])


# ---------------------------------------------------------------------------
# remove_note_tags
# ---------------------------------------------------------------------------

class TestRemoveNoteTags:
    def test_removes_existing_tags(self, service):
        service.create_note("N")
        service.add_note_tags("N", ["x", "y"])
        removed = service.remove_note_tags("N", ["x"])
        assert removed == ["x"]
        assert len(service.get_note("N").tags) == 1

    def test_ignores_missing_tags(self, service):
        service.create_note("N")
        service.add_note_tags("N", ["x"])
        removed = service.remove_note_tags("N", ["z"])
        assert removed == []

    def test_missing_note_raises(self, service):
        with pytest.raises(NoteNotFoundError):
            service.remove_note_tags("Ghost", ["tag"])


# ---------------------------------------------------------------------------
# delete_note
# ---------------------------------------------------------------------------

class TestDeleteNote:
    def test_deletes_note(self, service):
        service.create_note("ToDelete")
        service.delete_note("ToDelete")
        assert service.get_note("ToDelete") is None

    def test_missing_note_raises(self, service):
        with pytest.raises(NoteNotFoundError):
            service.delete_note("Ghost")


# ---------------------------------------------------------------------------
# rename_note
# ---------------------------------------------------------------------------

class TestRenameNote:
    def test_renames_note(self, service):
        service.create_note("Old")
        result = service.rename_note("Old", "New")
        assert result == "renamed"
        assert service.get_note("New") is not None
        assert service.get_note("Old") is None

    def test_same_name_returns_skipped(self, service):
        service.create_note("Same")
        result = service.rename_note("Same", "Same")
        assert result == "skipped"

    def test_missing_note_raises(self, service):
        with pytest.raises(NoteNotFoundError):
            service.rename_note("Ghost", "NewName")

    def test_target_name_exists_raises(self, service):
        service.create_note("A")
        service.create_note("B")
        with pytest.raises(NoteAlreadyExistsError):
            service.rename_note("A", "B")

    def test_renamed_note_preserves_content(self, service):
        service.create_note("Old", "important content")
        service.rename_note("Old", "New")
        assert service.get_note("New").content.value == "important content"


# ---------------------------------------------------------------------------
# search_notes
# ---------------------------------------------------------------------------

class TestSearchNotes:
    def test_finds_by_name(self, populated_service):
        results = populated_service.search_notes("Alpha", score_cutoff=50)
        names = [r.note.name.value for r in results]
        assert "Alpha" in names

    def test_finds_by_content(self, populated_service):
        results = populated_service.search_notes("beta", score_cutoff=50)
        names = [r.note.name.value for r in results]
        assert "Beta" in names

    def test_empty_query_returns_empty_or_all(self, populated_service):
        # Very low score matches could appear; just ensure no exception
        populated_service.search_notes("", score_cutoff=0)

    def test_no_match_returns_empty(self, populated_service):
        results = populated_service.search_notes("zzzzzzzzzzzz", score_cutoff=90)
        assert results == []

    def test_respects_limit(self, populated_service):
        results = populated_service.search_notes("a", score_cutoff=0, limit=2)
        assert len(results) <= 2

    def test_results_sorted_by_score_descending(self, populated_service):
        results = populated_service.search_notes("Alpha", score_cutoff=0)
        scores = [r.best_score for r in results]
        assert scores == sorted(scores, reverse=True)


# ---------------------------------------------------------------------------
# search_notes_by_tag
# ---------------------------------------------------------------------------

class TestSearchNotesByTag:
    def test_finds_notes_with_tag(self, service):
        service.create_note("N1")
        service.add_note_tags("N1", ["python"])
        service.create_note("N2")
        service.add_note_tags("N2", ["python", "work"])
        service.create_note("N3")
        service.add_note_tags("N3", ["work"])
        results = service.search_notes_by_tag("python")
        names = [n.name.value for n in results]
        assert "N1" in names
        assert "N2" in names
        assert "N3" not in names

    def test_no_matching_tag_returns_empty(self, service):
        service.create_note("N1")
        service.add_note_tags("N1", ["python"])
        assert service.search_notes_by_tag("ruby") == []


# ---------------------------------------------------------------------------
# list_note_tags
# ---------------------------------------------------------------------------

class TestListNoteTags:
    def test_counts_tags(self, service):
        service.create_note("N1")
        service.add_note_tags("N1", ["a", "b"])
        service.create_note("N2")
        service.add_note_tags("N2", ["a"])
        result = dict(service.list_note_tags())
        assert result["a"] == 2
        assert result["b"] == 1

    def test_sorted_alphabetically(self, service):
        service.create_note("N1")
        service.add_note_tags("N1", ["z", "a", "m"])
        tags = [t for t, _ in service.list_note_tags()]
        assert tags == sorted(tags)

    def test_empty_book_returns_empty(self, service):
        assert service.list_note_tags() == []



