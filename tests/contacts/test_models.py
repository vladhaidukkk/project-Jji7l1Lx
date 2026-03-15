import pytest
from datetime import datetime

from bot.contacts.models import (
    Address,
    Birthday,
    ContactRecord,
    ContactsBook,
    Email,
    Name,
    Phone,
)

pytestmark = [pytest.mark.contacts, pytest.mark.models]


# ---------------------------------------------------------------------------
# Name
# ---------------------------------------------------------------------------

class TestName:
    def test_valid_name(self):
        n = Name("Alice")
        assert n.value == "Alice"

    def test_strips_whitespace(self):
        n = Name("  Bob  ")
        assert n.value == "Bob"

    def test_empty_raises(self):
        with pytest.raises(ValueError):
            Name("")

    def test_whitespace_only_raises(self):
        with pytest.raises(ValueError):
            Name("   ")

    def test_str(self):
        assert str(Name("Alice")) == "Alice"

    def test_setter_strips_and_validates(self):
        n = Name("old")
        n.value = "  new  "
        assert n.value == "new"

    def test_setter_empty_raises(self):
        n = Name("old")
        with pytest.raises(ValueError):
            n.value = ""


# ---------------------------------------------------------------------------
# Phone
# ---------------------------------------------------------------------------

class TestPhone:
    def test_valid_phone(self):
        p = Phone("1234567890")
        assert p.value == "1234567890"

    def test_strips_whitespace(self):
        p = Phone("  1234567890  ")
        assert p.value == "1234567890"

    def test_empty_raises(self):
        with pytest.raises(ValueError):
            Phone("")

    def test_not_10_digits_raises(self):
        with pytest.raises(ValueError):
            Phone("12345")

    def test_non_digit_raises(self):
        with pytest.raises(ValueError):
            Phone("123456789a")

    def test_label(self):
        p = Phone("1234567890", label="mobile")
        assert p.label == "mobile"

    def test_label_strips_whitespace(self):
        p = Phone("1234567890", label="  work  ")
        assert p.label == "work"

    def test_empty_label_treated_as_none(self):
        p = Phone("1234567890", label="")
        assert p.label is None

    def test_no_label(self):
        p = Phone("1234567890")
        assert p.label is None

    def test_str_with_label(self):
        p = Phone("1234567890", label="home")
        assert str(p) == "1234567890 (home)"

    def test_str_without_label(self):
        p = Phone("1234567890")
        assert str(p) == "1234567890"

    def test_setter_validates(self):
        p = Phone("1234567890")
        with pytest.raises(ValueError):
            p.value = "short"


# ---------------------------------------------------------------------------
# Birthday
# ---------------------------------------------------------------------------

class TestBirthday:
    def test_valid_birthday(self):
        b = Birthday("15.03.1990")
        assert b.value == datetime(1990, 3, 15)

    def test_strips_whitespace(self):
        b = Birthday("  15.03.1990  ")
        assert b.value == datetime(1990, 3, 15)

    def test_invalid_format_raises(self):
        with pytest.raises(ValueError):
            Birthday("1990-03-15")

    def test_nonsense_raises(self):
        with pytest.raises(ValueError):
            Birthday("not-a-date")

    def test_str_format(self):
        b = Birthday("15.03.1990")
        assert str(b) == "1990.03.15"


# ---------------------------------------------------------------------------
# Email
# ---------------------------------------------------------------------------

class TestEmail:
    def test_valid_email(self):
        e = Email("test@example.com")
        assert e.value == "test@example.com"

    def test_strips_whitespace(self):
        e = Email("  test@example.com  ")
        assert e.value == "test@example.com"

    def test_empty_raises(self):
        with pytest.raises(ValueError):
            Email("")

    def test_invalid_format_raises(self):
        with pytest.raises(ValueError):
            Email("not-an-email")

    def test_label(self):
        e = Email("a@b.com", label="work")
        assert e.label == "work"

    def test_label_strips_whitespace(self):
        e = Email("a@b.com", label="  personal  ")
        assert e.label == "personal"

    def test_empty_label_treated_as_none(self):
        e = Email("a@b.com", label="")
        assert e.label is None

    def test_no_label(self):
        e = Email("a@b.com")
        assert e.label is None

    def test_str_with_label(self):
        e = Email("a@b.com", label="work")
        assert str(e) == "a@b.com (work)"

    def test_str_without_label(self):
        e = Email("a@b.com")
        assert str(e) == "a@b.com"

    def test_setter_validates(self):
        e = Email("a@b.com")
        with pytest.raises(ValueError):
            e.value = "bad"


# ---------------------------------------------------------------------------
# Address
# ---------------------------------------------------------------------------

class TestAddress:
    def test_valid_address(self):
        a = Address("123 Main St")
        assert a.value == "123 Main St"

    def test_strips_whitespace(self):
        a = Address("  123 Main St  ")
        assert a.value == "123 Main St"

    def test_empty_raises(self):
        with pytest.raises(ValueError):
            Address("")

    def test_whitespace_only_raises(self):
        with pytest.raises(ValueError):
            Address("   ")

    def test_label(self):
        a = Address("123 Main St", label="home")
        assert a.label == "home"

    def test_empty_label_treated_as_none(self):
        a = Address("123 Main St", label="")
        assert a.label is None

    def test_no_label(self):
        a = Address("123 Main St")
        assert a.label is None

    def test_str_with_label(self):
        a = Address("123 Main St", label="home")
        assert str(a) == "123 Main St (home)"

    def test_str_without_label(self):
        a = Address("123 Main St")
        assert str(a) == "123 Main St"

    def test_setter_validates(self):
        a = Address("123 Main St")
        with pytest.raises(ValueError):
            a.value = ""


# ---------------------------------------------------------------------------
# ContactRecord
# ---------------------------------------------------------------------------

class TestContactRecord:
    # -- init --
    def test_init(self):
        c = ContactRecord("Alice")
        assert c.name.value == "Alice"
        assert c.phones == []
        assert c.birthday is None
        assert c.emails == []
        assert c.addresses == []
        assert c.is_favorite is False

    # -- phones --
    def test_add_phone(self):
        c = ContactRecord("A")
        c.add_phone("1234567890")
        assert len(c.phones) == 1
        assert c.phones[0].value == "1234567890"

    def test_add_duplicate_phone_raises(self):
        c = ContactRecord("A")
        c.add_phone("1234567890")
        with pytest.raises(ValueError):
            c.add_phone("1234567890")

    def test_remove_phone(self):
        c = ContactRecord("A")
        c.add_phone("1234567890")
        c.remove_phone("1234567890")
        assert c.phones == []

    def test_remove_missing_phone_raises(self):
        c = ContactRecord("A")
        with pytest.raises(ValueError):
            c.remove_phone("0000000000")

    def test_edit_phone(self):
        c = ContactRecord("A")
        c.add_phone("1234567890")
        c.edit_phone("1234567890", "0987654321")
        assert c.phones[0].value == "0987654321"

    def test_edit_phone_same_raises(self):
        c = ContactRecord("A")
        c.add_phone("1234567890")
        with pytest.raises(ValueError):
            c.edit_phone("1234567890", "1234567890")

    def test_edit_phone_old_missing_raises(self):
        c = ContactRecord("A")
        with pytest.raises(ValueError):
            c.edit_phone("1234567890", "0987654321")

    def test_edit_phone_new_exists_raises(self):
        c = ContactRecord("A")
        c.add_phone("1234567890")
        c.add_phone("0987654321")
        with pytest.raises(ValueError):
            c.edit_phone("1234567890", "0987654321")

    def test_edit_phone_preserves_label(self):
        c = ContactRecord("A")
        c.add_phone("1234567890")
        c.add_phone_label("1234567890", "mobile")
        c.edit_phone("1234567890", "0987654321")
        assert c.phones[0].label == "mobile"

    def test_add_phone_label(self):
        c = ContactRecord("A")
        c.add_phone("1234567890")
        c.add_phone_label("1234567890", "work")
        assert c.find_phone("1234567890").label == "work"

    def test_add_phone_label_missing_phone_raises(self):
        c = ContactRecord("A")
        with pytest.raises(ValueError):
            c.add_phone_label("0000000000", "x")

    def test_remove_phone_label(self):
        c = ContactRecord("A")
        c.add_phone("1234567890")
        c.add_phone_label("1234567890", "work")
        c.remove_phone_label("1234567890")
        assert c.find_phone("1234567890").label is None

    def test_remove_phone_label_no_label_raises(self):
        c = ContactRecord("A")
        c.add_phone("1234567890")
        with pytest.raises(ValueError):
            c.remove_phone_label("1234567890")

    def test_find_phone(self):
        c = ContactRecord("A")
        c.add_phone("1234567890")
        assert c.find_phone("1234567890").value == "1234567890"

    def test_find_phone_missing(self):
        c = ContactRecord("A")
        assert c.find_phone("0000000000") is None

    # -- birthday --
    def test_add_birthday(self):
        c = ContactRecord("A")
        c.add_birthday("15.03.1990")
        assert c.birthday is not None

    def test_add_birthday_overwrites(self):
        c = ContactRecord("A")
        c.add_birthday("15.03.1990")
        c.add_birthday("01.01.2000")
        assert c.birthday.value == datetime(2000, 1, 1)

    def test_remove_birthday(self):
        c = ContactRecord("A")
        c.add_birthday("15.03.1990")
        c.remove_birthday()
        assert c.birthday is None

    def test_remove_birthday_not_set_raises(self):
        c = ContactRecord("A")
        with pytest.raises(ValueError):
            c.remove_birthday()

    # -- emails --
    def test_add_email(self):
        c = ContactRecord("A")
        c.add_email("a@b.com")
        assert len(c.emails) == 1

    def test_add_duplicate_email_raises(self):
        c = ContactRecord("A")
        c.add_email("a@b.com")
        with pytest.raises(ValueError):
            c.add_email("a@b.com")

    def test_remove_email(self):
        c = ContactRecord("A")
        c.add_email("a@b.com")
        c.remove_email("a@b.com")
        assert c.emails == []

    def test_remove_missing_email_raises(self):
        c = ContactRecord("A")
        with pytest.raises(ValueError):
            c.remove_email("a@b.com")

    def test_edit_email(self):
        c = ContactRecord("A")
        c.add_email("a@b.com")
        c.edit_email("a@b.com", "x@y.com")
        assert c.emails[0].value == "x@y.com"

    def test_edit_email_same_raises(self):
        c = ContactRecord("A")
        c.add_email("a@b.com")
        with pytest.raises(ValueError):
            c.edit_email("a@b.com", "a@b.com")

    def test_edit_email_old_missing_raises(self):
        c = ContactRecord("A")
        with pytest.raises(ValueError):
            c.edit_email("a@b.com", "x@y.com")

    def test_edit_email_new_exists_raises(self):
        c = ContactRecord("A")
        c.add_email("a@b.com")
        c.add_email("x@y.com")
        with pytest.raises(ValueError):
            c.edit_email("a@b.com", "x@y.com")

    def test_edit_email_preserves_label(self):
        c = ContactRecord("A")
        c.add_email("a@b.com")
        c.add_email_label("a@b.com", "work")
        c.edit_email("a@b.com", "x@y.com")
        assert c.emails[0].label == "work"

    def test_add_email_label(self):
        c = ContactRecord("A")
        c.add_email("a@b.com")
        c.add_email_label("a@b.com", "work")
        assert c.find_email("a@b.com").label == "work"

    def test_add_email_label_missing_raises(self):
        c = ContactRecord("A")
        with pytest.raises(ValueError):
            c.add_email_label("a@b.com", "x")

    def test_remove_email_label(self):
        c = ContactRecord("A")
        c.add_email("a@b.com")
        c.add_email_label("a@b.com", "work")
        c.remove_email_label("a@b.com")
        assert c.find_email("a@b.com").label is None

    def test_remove_email_label_no_label_raises(self):
        c = ContactRecord("A")
        c.add_email("a@b.com")
        with pytest.raises(ValueError):
            c.remove_email_label("a@b.com")

    def test_find_email(self):
        c = ContactRecord("A")
        c.add_email("a@b.com")
        assert c.find_email("a@b.com").value == "a@b.com"

    def test_find_email_missing(self):
        c = ContactRecord("A")
        assert c.find_email("a@b.com") is None

    # -- addresses --
    def test_add_address(self):
        c = ContactRecord("A")
        c.add_address("123 Main St")
        assert len(c.addresses) == 1

    def test_add_duplicate_address_raises(self):
        c = ContactRecord("A")
        c.add_address("123 Main St")
        with pytest.raises(ValueError):
            c.add_address("123 Main St")

    def test_remove_address(self):
        c = ContactRecord("A")
        c.add_address("123 Main St")
        c.remove_address("123 Main St")
        assert c.addresses == []

    def test_remove_missing_address_raises(self):
        c = ContactRecord("A")
        with pytest.raises(ValueError):
            c.remove_address("123 Main St")

    def test_edit_address(self):
        c = ContactRecord("A")
        c.add_address("123 Main St")
        c.edit_address("123 Main St", "456 Oak Ave")
        assert c.addresses[0].value == "456 Oak Ave"

    def test_edit_address_same_raises(self):
        c = ContactRecord("A")
        c.add_address("123 Main St")
        with pytest.raises(ValueError):
            c.edit_address("123 Main St", "123 Main St")

    def test_edit_address_old_missing_raises(self):
        c = ContactRecord("A")
        with pytest.raises(ValueError):
            c.edit_address("123 Main St", "456 Oak Ave")

    def test_edit_address_new_exists_raises(self):
        c = ContactRecord("A")
        c.add_address("123 Main St")
        c.add_address("456 Oak Ave")
        with pytest.raises(ValueError):
            c.edit_address("123 Main St", "456 Oak Ave")

    def test_edit_address_preserves_label(self):
        c = ContactRecord("A")
        c.add_address("123 Main St")
        c.add_address_label("123 Main St", "home")
        c.edit_address("123 Main St", "456 Oak Ave")
        assert c.addresses[0].label == "home"

    def test_add_address_label(self):
        c = ContactRecord("A")
        c.add_address("123 Main St")
        c.add_address_label("123 Main St", "home")
        assert c.find_address("123 Main St").label == "home"

    def test_add_address_label_missing_raises(self):
        c = ContactRecord("A")
        with pytest.raises(ValueError):
            c.add_address_label("123 Main St", "x")

    def test_remove_address_label(self):
        c = ContactRecord("A")
        c.add_address("123 Main St")
        c.add_address_label("123 Main St", "home")
        c.remove_address_label("123 Main St")
        assert c.find_address("123 Main St").label is None

    def test_remove_address_label_no_label_raises(self):
        c = ContactRecord("A")
        c.add_address("123 Main St")
        with pytest.raises(ValueError):
            c.remove_address_label("123 Main St")

    def test_find_address(self):
        c = ContactRecord("A")
        c.add_address("123 Main St")
        assert c.find_address("123 Main St").value == "123 Main St"

    def test_find_address_missing(self):
        c = ContactRecord("A")
        assert c.find_address("123 Main St") is None

    # -- favorites --
    def test_mark_favorite(self):
        c = ContactRecord("A")
        c.mark_favorite()
        assert c.is_favorite is True

    def test_unmark_favorite(self):
        c = ContactRecord("A")
        c.mark_favorite()
        c.unmark_favorite()
        assert c.is_favorite is False

    # -- __str__ --
    def test_str_minimal(self):
        c = ContactRecord("Alice")
        result = str(c)
        assert "Alice" in result

    def test_str_favorite_prefix(self):
        c = ContactRecord("Alice")
        c.mark_favorite()
        assert str(c).startswith("* ")

    def test_str_includes_phone(self):
        c = ContactRecord("Alice")
        c.add_phone("1234567890")
        assert "1234567890" in str(c)

    def test_str_includes_email(self):
        c = ContactRecord("Alice")
        c.add_email("a@b.com")
        assert "a@b.com" in str(c)

    def test_str_includes_address(self):
        c = ContactRecord("Alice")
        c.add_address("123 Main St")
        assert "123 Main St" in str(c)

    def test_str_includes_birthday(self):
        c = ContactRecord("Alice")
        c.add_birthday("15.03.1990")
        assert "1990.03.15" in str(c)


# ---------------------------------------------------------------------------
# ContactsBook
# ---------------------------------------------------------------------------

class TestContactsBook:
    def test_add_and_find(self):
        book = ContactsBook()
        rec = ContactRecord("Alice")
        book.add_record(rec)
        assert book.find("Alice") is rec

    def test_find_missing_returns_none(self):
        book = ContactsBook()
        assert book.find("Ghost") is None

    def test_delete_existing(self):
        book = ContactsBook()
        book.add_record(ContactRecord("Alice"))
        book.delete("Alice")
        assert book.find("Alice") is None

    def test_delete_missing_raises(self):
        book = ContactsBook()
        with pytest.raises(KeyError):
            book.delete("Ghost")

    def test_birthdays_count(self):
        book = ContactsBook()
        r1 = ContactRecord("A")
        r1.add_birthday("01.01.2000")
        r2 = ContactRecord("B")
        book.add_record(r1)
        book.add_record(r2)
        assert book.birthdays_count == 1

    def test_birthdays_count_empty(self):
        book = ContactsBook()
        assert book.birthdays_count == 0

    def test_get_upcoming_birthdays_returns_list(self):
        book = ContactsBook()
        result = book.get_upcoming_birthdays(7)
        assert isinstance(result, list)

    def test_from_file_missing_returns_empty(self, tmp_path):
        book = ContactsBook.from_file(tmp_path / "missing.pkl")
        assert isinstance(book, ContactsBook)
        assert len(book.data) == 0

    def test_save_and_load_roundtrip(self, tmp_path):
        path = tmp_path / "contacts.pkl"
        book = ContactsBook()
        rec = ContactRecord("Alice")
        rec.add_phone("1234567890")
        rec.add_email("a@b.com")
        book.add_record(rec)
        book.save(path)

        loaded = ContactsBook.from_file(path)
        contact = loaded.find("Alice")
        assert contact is not None
        assert contact.phones[0].value == "1234567890"
        assert contact.emails[0].value == "a@b.com"

