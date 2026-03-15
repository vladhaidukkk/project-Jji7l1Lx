import pytest

from bot.contacts.errors import ContactAlreadyExistsError, ContactNotFoundError
from bot.contacts.models import ContactsBook
from bot.contacts.service import ContactsService

pytestmark = [pytest.mark.contacts, pytest.mark.service]


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def book() -> ContactsBook:
    return ContactsBook()


@pytest.fixture
def service(book: ContactsBook) -> ContactsService:
    return ContactsService(book)


# ---------------------------------------------------------------------------
# create_contact
# ---------------------------------------------------------------------------

class TestCreateContact:
    def test_creates_contact(self, service):
        service.create_contact("Alice")
        assert service.get_contact("Alice") is not None

    def test_creates_with_phone(self, service):
        service.create_contact("Alice", phone="1234567890")
        assert service.get_contact("Alice").phones[0].value == "1234567890"

    def test_creates_with_birthday(self, service):
        service.create_contact("Alice", birthday="15.03.1990")
        assert service.get_contact("Alice").birthday is not None

    def test_creates_with_email(self, service):
        service.create_contact("Alice", email="a@b.com")
        assert service.get_contact("Alice").emails[0].value == "a@b.com"

    def test_creates_with_address(self, service):
        service.create_contact("Alice", address="123 Main St")
        assert service.get_contact("Alice").addresses[0].value == "123 Main St"

    def test_duplicate_raises(self, service):
        service.create_contact("Alice")
        with pytest.raises(ContactAlreadyExistsError):
            service.create_contact("Alice")


# ---------------------------------------------------------------------------
# get_contact
# ---------------------------------------------------------------------------

class TestGetContact:
    def test_returns_contact(self, service):
        service.create_contact("Alice")
        assert service.get_contact("Alice") is not None

    def test_returns_none_for_missing(self, service):
        assert service.get_contact("Ghost") is None


# ---------------------------------------------------------------------------
# add_phone / delete_phone
# ---------------------------------------------------------------------------

class TestPhone:
    def test_add_phone(self, service):
        service.create_contact("Alice")
        service.add_phone("Alice", phone="1234567890")
        assert len(service.get_contact("Alice").phones) == 1

    def test_add_phone_missing_contact_raises(self, service):
        with pytest.raises(ContactNotFoundError):
            service.add_phone("Ghost", phone="1234567890")

    def test_delete_phone(self, service):
        service.create_contact("Alice", phone="1234567890")
        service.delete_phone("Alice", phone="1234567890")
        assert service.get_contact("Alice").phones == []

    def test_delete_phone_missing_contact_raises(self, service):
        with pytest.raises(ContactNotFoundError):
            service.delete_phone("Ghost", phone="1234567890")

    def test_delete_phone_missing_phone_raises(self, service):
        service.create_contact("Alice")
        with pytest.raises(ValueError):
            service.delete_phone("Alice", phone="0000000000")


# ---------------------------------------------------------------------------
# add_phone_label / delete_phone_label
# ---------------------------------------------------------------------------

class TestPhoneLabel:
    def test_add_phone_label(self, service):
        service.create_contact("Alice", phone="1234567890")
        service.add_phone_label("Alice", phone="1234567890", label="mobile")
        assert service.get_contact("Alice").find_phone("1234567890").label == "mobile"

    def test_add_phone_label_missing_contact_raises(self, service):
        with pytest.raises(ContactNotFoundError):
            service.add_phone_label("Ghost", phone="1234567890", label="x")

    def test_delete_phone_label(self, service):
        service.create_contact("Alice", phone="1234567890")
        service.add_phone_label("Alice", phone="1234567890", label="mobile")
        service.delete_phone_label("Alice", phone="1234567890")
        assert service.get_contact("Alice").find_phone("1234567890").label is None

    def test_delete_phone_label_missing_contact_raises(self, service):
        with pytest.raises(ContactNotFoundError):
            service.delete_phone_label("Ghost", phone="1234567890")


# ---------------------------------------------------------------------------
# add_birthday / delete_birthday
# ---------------------------------------------------------------------------

class TestBirthday:
    def test_add_birthday_returns_added(self, service):
        service.create_contact("Alice")
        result = service.add_birthday("Alice", birthday="15.03.1990")
        assert result == "added"

    def test_add_birthday_returns_updated(self, service):
        service.create_contact("Alice", birthday="15.03.1990")
        result = service.add_birthday("Alice", birthday="01.01.2000")
        assert result == "updated"

    def test_add_birthday_missing_contact_raises(self, service):
        with pytest.raises(ContactNotFoundError):
            service.add_birthday("Ghost", birthday="15.03.1990")

    def test_delete_birthday(self, service):
        service.create_contact("Alice", birthday="15.03.1990")
        service.delete_birthday("Alice")
        assert service.get_contact("Alice").birthday is None

    def test_delete_birthday_missing_contact_raises(self, service):
        with pytest.raises(ContactNotFoundError):
            service.delete_birthday("Ghost")

    def test_delete_birthday_not_set_raises(self, service):
        service.create_contact("Alice")
        with pytest.raises(ValueError):
            service.delete_birthday("Alice")


# ---------------------------------------------------------------------------
# add_email / delete_email / change_email
# ---------------------------------------------------------------------------

class TestEmail:
    def test_add_email(self, service):
        service.create_contact("Alice")
        service.add_email("Alice", email="a@b.com")
        assert len(service.get_contact("Alice").emails) == 1

    def test_add_email_missing_contact_raises(self, service):
        with pytest.raises(ContactNotFoundError):
            service.add_email("Ghost", email="a@b.com")

    def test_delete_email(self, service):
        service.create_contact("Alice", email="a@b.com")
        service.delete_email("Alice", email="a@b.com")
        assert service.get_contact("Alice").emails == []

    def test_delete_email_missing_contact_raises(self, service):
        with pytest.raises(ContactNotFoundError):
            service.delete_email("Ghost", email="a@b.com")

    def test_change_email(self, service):
        service.create_contact("Alice", email="a@b.com")
        service.change_email("Alice", old_email="a@b.com", new_email="x@y.com")
        assert service.get_contact("Alice").emails[0].value == "x@y.com"

    def test_change_email_missing_contact_raises(self, service):
        with pytest.raises(ContactNotFoundError):
            service.change_email("Ghost", old_email="a@b.com", new_email="x@y.com")


# ---------------------------------------------------------------------------
# add_email_label / delete_email_label
# ---------------------------------------------------------------------------

class TestEmailLabel:
    def test_add_email_label(self, service):
        service.create_contact("Alice", email="a@b.com")
        service.add_email_label("Alice", email="a@b.com", label="work")
        assert service.get_contact("Alice").find_email("a@b.com").label == "work"

    def test_add_email_label_missing_contact_raises(self, service):
        with pytest.raises(ContactNotFoundError):
            service.add_email_label("Ghost", email="a@b.com", label="x")

    def test_delete_email_label(self, service):
        service.create_contact("Alice", email="a@b.com")
        service.add_email_label("Alice", email="a@b.com", label="work")
        service.delete_email_label("Alice", email="a@b.com")
        assert service.get_contact("Alice").find_email("a@b.com").label is None

    def test_delete_email_label_missing_contact_raises(self, service):
        with pytest.raises(ContactNotFoundError):
            service.delete_email_label("Ghost", email="a@b.com")


# ---------------------------------------------------------------------------
# add_address / delete_address / change_address
# ---------------------------------------------------------------------------

class TestAddress:
    def test_add_address(self, service):
        service.create_contact("Alice")
        service.add_address("Alice", address="123 Main St")
        assert len(service.get_contact("Alice").addresses) == 1

    def test_add_address_missing_contact_raises(self, service):
        with pytest.raises(ContactNotFoundError):
            service.add_address("Ghost", address="123 Main St")

    def test_delete_address(self, service):
        service.create_contact("Alice", address="123 Main St")
        service.delete_address("Alice", address="123 Main St")
        assert service.get_contact("Alice").addresses == []

    def test_delete_address_missing_contact_raises(self, service):
        with pytest.raises(ContactNotFoundError):
            service.delete_address("Ghost", address="123 Main St")

    def test_change_address(self, service):
        service.create_contact("Alice", address="123 Main St")
        service.change_address("Alice", old_address="123 Main St", new_address="456 Oak Ave")
        assert service.get_contact("Alice").addresses[0].value == "456 Oak Ave"

    def test_change_address_missing_contact_raises(self, service):
        with pytest.raises(ContactNotFoundError):
            service.change_address("Ghost", old_address="123 Main St", new_address="456 Oak Ave")


# ---------------------------------------------------------------------------
# add_address_label / delete_address_label
# ---------------------------------------------------------------------------

class TestAddressLabel:
    def test_add_address_label(self, service):
        service.create_contact("Alice", address="123 Main St")
        service.add_address_label("Alice", address="123 Main St", label="home")
        assert service.get_contact("Alice").find_address("123 Main St").label == "home"

    def test_add_address_label_missing_contact_raises(self, service):
        with pytest.raises(ContactNotFoundError):
            service.add_address_label("Ghost", address="123 Main St", label="x")

    def test_delete_address_label(self, service):
        service.create_contact("Alice", address="123 Main St")
        service.add_address_label("Alice", address="123 Main St", label="home")
        service.delete_address_label("Alice", address="123 Main St")
        assert service.get_contact("Alice").find_address("123 Main St").label is None

    def test_delete_address_label_missing_contact_raises(self, service):
        with pytest.raises(ContactNotFoundError):
            service.delete_address_label("Ghost", address="123 Main St")


# ---------------------------------------------------------------------------
# mark_favorite / unmark_favorite
# ---------------------------------------------------------------------------

class TestFavorite:
    def test_mark_favorite(self, service):
        service.create_contact("Alice")
        service.mark_favorite("Alice")
        assert service.get_contact("Alice").is_favorite is True

    def test_mark_favorite_missing_raises(self, service):
        with pytest.raises(ContactNotFoundError):
            service.mark_favorite("Ghost")

    def test_unmark_favorite(self, service):
        service.create_contact("Alice")
        service.mark_favorite("Alice")
        service.unmark_favorite("Alice")
        assert service.get_contact("Alice").is_favorite is False

    def test_unmark_favorite_missing_raises(self, service):
        with pytest.raises(ContactNotFoundError):
            service.unmark_favorite("Ghost")


# ---------------------------------------------------------------------------
# update_contact
# ---------------------------------------------------------------------------

class TestUpdateContact:
    def test_update_phone(self, service):
        service.create_contact("Alice", phone="1234567890")
        service.update_contact("Alice", phone=("1234567890", "0987654321"))
        assert service.get_contact("Alice").phones[0].value == "0987654321"

    def test_update_birthday(self, service):
        service.create_contact("Alice", birthday="15.03.1990")
        service.update_contact("Alice", birthday="01.01.2000")
        from datetime import datetime
        assert service.get_contact("Alice").birthday.value == datetime(2000, 1, 1)

    def test_update_email(self, service):
        service.create_contact("Alice", email="a@b.com")
        service.update_contact("Alice", email=("a@b.com", "x@y.com"))
        assert service.get_contact("Alice").emails[0].value == "x@y.com"

    def test_update_address(self, service):
        service.create_contact("Alice", address="123 Main St")
        service.update_contact("Alice", address=("123 Main St", "456 Oak Ave"))
        assert service.get_contact("Alice").addresses[0].value == "456 Oak Ave"

    def test_update_missing_contact_raises(self, service):
        with pytest.raises(ContactNotFoundError):
            service.update_contact("Ghost", birthday="01.01.2000")


# ---------------------------------------------------------------------------
# delete_contact
# ---------------------------------------------------------------------------

class TestDeleteContact:
    def test_deletes_contact(self, service):
        service.create_contact("Alice")
        service.delete_contact("Alice")
        assert service.get_contact("Alice") is None

    def test_missing_raises(self, service):
        with pytest.raises(ContactNotFoundError):
            service.delete_contact("Ghost")


# ---------------------------------------------------------------------------
# rename_contact
# ---------------------------------------------------------------------------

class TestRenameContact:
    def test_renames(self, service):
        service.create_contact("Alice")
        result = service.rename_contact("Alice", "Bob")
        assert result == "renamed"
        assert service.get_contact("Bob") is not None
        assert service.get_contact("Alice") is None

    def test_same_name_returns_skipped(self, service):
        service.create_contact("Alice")
        result = service.rename_contact("Alice", "Alice")
        assert result == "skipped"

    def test_missing_raises(self, service):
        with pytest.raises(ContactNotFoundError):
            service.rename_contact("Ghost", "NewName")

    def test_target_exists_raises(self, service):
        service.create_contact("Alice")
        service.create_contact("Bob")
        with pytest.raises(ContactAlreadyExistsError):
            service.rename_contact("Alice", "Bob")

    def test_preserves_data(self, service):
        service.create_contact("Alice", phone="1234567890", email="a@b.com")
        service.rename_contact("Alice", "Bob")
        contact = service.get_contact("Bob")
        assert contact.phones[0].value == "1234567890"
        assert contact.emails[0].value == "a@b.com"


# ---------------------------------------------------------------------------
# search_contacts_by_field
# ---------------------------------------------------------------------------

class TestSearchContacts:
    def test_search_by_name(self, service):
        service.create_contact("Alice")
        service.create_contact("Bob")
        results = service.search_contacts_by_field("Alice", "name", score_cutoff=50)
        names = [r.contact.name.value for r in results]
        assert "Alice" in names

    def test_search_by_phone(self, service):
        service.create_contact("Alice", phone="1234567890")
        results = service.search_contacts_by_field("1234567890", "phone", score_cutoff=50)
        names = [r.contact.name.value for r in results]
        assert "Alice" in names

    def test_search_by_email(self, service):
        service.create_contact("Alice", email="alice@example.com")
        results = service.search_contacts_by_field("alice@example.com", "email", score_cutoff=50)
        names = [r.contact.name.value for r in results]
        assert "Alice" in names

    def test_search_by_address(self, service):
        service.create_contact("Alice", address="123 Main St")
        results = service.search_contacts_by_field("123 Main", "address", score_cutoff=50)
        names = [r.contact.name.value for r in results]
        assert "Alice" in names

    def test_search_no_match(self, service):
        service.create_contact("Alice")
        results = service.search_contacts_by_field("zzzzzzzz", "name", score_cutoff=90)
        assert results == []

    def test_search_respects_limit(self, service):
        for i in range(10):
            service.create_contact(f"Contact{i}")
        results = service.search_contacts_by_field("Contact", "name", score_cutoff=0, limit=3)
        assert len(results) <= 3

