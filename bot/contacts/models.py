import pickle
import re
from collections import UserDict
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Self

from bot.common import Field
from bot.utils.file_utils import ensure_file_dir_exists

EMAIL_PATTERN = re.compile(r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$")


class Name(Field):
    def __init__(self, value: str) -> None:
        """Initialise and validate a contact name.

        Args:
            value: The contact's name. Leading/trailing whitespace is stripped.

        Raises:
            ValueError: If the stripped value is empty.
        """
        value_stripped = value.strip()
        super().__init__(value_stripped)
        self.value = value_stripped

    @property
    def value(self) -> str:
        """The stored name string.

        Returns:
            The validated, stripped name value.
        """
        return self._value

    @value.setter
    def value(self, value: str) -> None:
        """Set and validate the name value.

        Args:
            value: New name string. Stripped before validation.

        Raises:
            ValueError: If the stripped value is empty.
        """
        value_stripped = value.strip()
        if not value_stripped:
            raise ValueError("Name cannot be empty")
        self._value = value_stripped


class Phone(Field):
    def __init__(self, value: str, label: str | None = None) -> None:
        """Initialise and validate a phone number.

        Args:
            value: A 10-digit phone number string.
            label: An optional descriptive label (e.g. "mobile"). Stripped and
                validated when provided.

        Raises:
            ValueError: If *value* is empty, not exactly 10 digits, or contains
                non-digit characters.
            ValueError: If *label* is provided but empty after stripping.
        """
        value_stripped = value.strip()
        super().__init__(value_stripped)
        self.value = value_stripped
        self.label = self._normalize_label(label) if label else None

    @property
    def value(self) -> str:
        """The stored phone number string.

        Returns:
            The validated 10-digit phone number.
        """
        return self._value

    @value.setter
    def value(self, value: str) -> None:
        """Set and validate the phone number.

        Args:
            value: New phone number string.

        Raises:
            ValueError: If *value* is empty, not exactly 10 digits, or contains
                non-digit characters.
        """
        value_stripped = value.strip()
        if not value_stripped:
            raise ValueError("Phone number cannot be empty")
        if len(value_stripped) != 10:
            raise ValueError("Phone number must be exactly 10 digits")
        if not value_stripped.isdigit():
            raise ValueError("Phone number must contain only digits")
        self._value = value_stripped

    @staticmethod
    def _normalize_label(label: str) -> str:
        """Strip and validate a phone label.

        Args:
            label: The raw label string to normalise.

        Returns:
            The stripped label string.

        Raises:
            ValueError: If the stripped label is empty.
        """
        label = label.strip()
        if not label:
            raise ValueError("Phone label cannot be empty")
        return label

    def __str__(self) -> str:
        """Return a string representation including the optional label.

        Returns:
            ``"<number> (<label>)"`` when a label is set, otherwise just
            ``"<number>"``.
        """
        return f"{self.value} ({self.label})" if self.label else self.value


class Birthday(Field):
    def __init__(self, value: str) -> None:
        """Initialise and parse a birthday from a DD.MM.YYYY string.

        Args:
            value: Birthday string in ``DD.MM.YYYY`` format.

        Raises:
            ValueError: If *value* does not match the expected format.
        """
        value_stripped = value.strip()
        super().__init__(value_stripped)
        self.value = value_stripped

    def __str__(self) -> str:
        """Return the birthday formatted as YYYY.MM.DD.

        Returns:
            A string in ``YYYY.MM.DD`` format.
        """
        return self.value.strftime("%Y.%m.%d")

    @property
    def value(self) -> str:
        """The stored birthday as a :class:`~datetime.datetime` object.

        Returns:
            The parsed datetime representing the birthday.
        """
        return self._value

    @value.setter
    def value(self, value: str) -> None:
        """Parse and store a birthday from a DD.MM.YYYY string.

        Args:
            value: Birthday string to parse.

        Raises:
            ValueError: If *value* cannot be parsed as ``DD.MM.YYYY``.
        """
        try:
            value_stripped = value.strip()
            value_parsed = datetime.strptime(value_stripped, "%d.%m.%Y")
            self._value = value_parsed
        except ValueError:
            raise ValueError("Invalid birthday format. Use DD.MM.YYYY")


class Email(Field):
    def __init__(self, value: str, label: str | None = None) -> None:
        """Initialise and validate an email address.

        Args:
            value: The email address string.
            label: An optional descriptive label (e.g. "work"). Stripped and
                validated when provided.

        Raises:
            ValueError: If *value* is empty or not a valid email address.
            ValueError: If *label* is provided but empty after stripping.
        """
        value_stripped = value.strip()
        super().__init__(value_stripped)
        self.value = value_stripped
        self.label = self._normalize_label(label) if label else None

    @staticmethod
    def _normalize_label(label: str) -> str:
        """Strip and validate an email label.

        Args:
            label: The raw label string to normalise.

        Returns:
            The stripped label string.

        Raises:
            ValueError: If the stripped label is empty.
        """
        label = label.strip()
        if not label:
            raise ValueError("Email label cannot be empty")
        return label

    def __str__(self) -> str:
        """Return a string representation including the optional label.

        Returns:
            ``"<email> (<label>)"`` when a label is set, otherwise just
            ``"<email>"``.
        """
        return f"{self.value} ({self.label})" if self.label else self.value

    @property
    def value(self) -> str:
        """The stored email address string.

        Returns:
            The validated email address.
        """
        return self._value

    @value.setter
    def value(self, value: str) -> None:
        """Set and validate the email address.

        Args:
            value: New email address string.

        Raises:
            ValueError: If *value* is empty or fails the email pattern check.
        """
        value_stripped = value.strip()
        if not value_stripped:
            raise ValueError("Email cannot be empty")
        if not EMAIL_PATTERN.fullmatch(value_stripped):
            raise ValueError("Invalid email format")
        self._value = value_stripped


class Address(Field):
    def __init__(self, value: str, label: str | None = None) -> None:
        """Initialise and validate a postal address.

        Args:
            value: The address string.
            label: An optional descriptive label (e.g. "home"). Stripped and
                validated when provided.

        Raises:
            ValueError: If *value* is empty after stripping.
            ValueError: If *label* is provided but empty after stripping.
        """
        value_stripped = value.strip()
        super().__init__(value_stripped)
        self.value = value_stripped
        self.label = self._normalize_label(label) if label else None

    @property
    def value(self) -> str:
        """The stored address string.

        Returns:
            The validated address value.
        """
        return self._value

    @value.setter
    def value(self, value: str) -> None:
        """Set and validate the address.

        Args:
            value: New address string.

        Raises:
            ValueError: If *value* is empty after stripping.
        """
        value_stripped = value.strip()
        if not value_stripped:
            raise ValueError("Address cannot be empty")
        self._value = value_stripped

    @staticmethod
    def _normalize_label(label: str) -> str:
        """Strip and validate an address label.

        Args:
            label: The raw label string to normalise.

        Returns:
            The stripped label string.

        Raises:
            ValueError: If the stripped label is empty.
        """
        label = label.strip()
        if not label:
            raise ValueError("Address label cannot be empty")
        return label

    def __str__(self) -> str:
        """Return a string representation including the optional label.

        Returns:
            ``"<address> (<label>)"`` when a label is set, otherwise just
            ``"<address>"``.
        """
        return f"{self.value} ({self.label})" if self.label else self.value


class ContactRecord:
    def __init__(self, name: str) -> None:
        """Initialise an empty contact record with the given name.

        Args:
            name: The contact's full name.
        """
        self.name = Name(name)
        self.phones: list[Phone] = []
        self.birthday: Birthday | None = None
        self.emails: list[Email] = []
        self.addresses: list[Address] = []
        self.is_favorite = False

    def add_phone(self, phone: str) -> None:
        """Add a phone number to the contact.

        Args:
            phone: The 10-digit phone number to add.

        Raises:
            ValueError: If *phone* already exists on the contact or is invalid.
        """
        phone_idx = self._find_phone_index(phone)
        if phone_idx is not None:
            raise ValueError(f"Phone number '{phone}' already exists")
        self.phones.append(Phone(phone))

    def remove_phone(self, phone: str) -> None:
        """Remove a phone number from the contact.

        Args:
            phone: The phone number to remove.

        Raises:
            ValueError: If *phone* does not exist on the contact.
        """
        phone_idx = self._find_phone_index(phone)
        if phone_idx is None:
            raise ValueError(f"Phone number '{phone}' does not exist")
        del self.phones[phone_idx]

    def edit_phone(self, old_phone: str, new_phone: str) -> None:
        """Replace an existing phone number with a new one.

        Args:
            old_phone: The phone number to replace.
            new_phone: The replacement phone number.

        Raises:
            ValueError: If *old_phone* equals *new_phone*, *old_phone* does not
                exist, or *new_phone* already exists on the contact.
        """
        if old_phone == new_phone:
            raise ValueError("New phone number must be different from the current one")
        phone_idx = self._find_phone_index(old_phone)
        if phone_idx is None:
            raise ValueError(f"Phone number '{old_phone}' does not exist")
        existing_phone_idx = self._find_phone_index(new_phone)
        if existing_phone_idx is not None:
            raise ValueError(f"Phone number '{new_phone}' already exists")
        self.phones[phone_idx] = Phone(new_phone, label=self.phones[phone_idx].label)

    def add_phone_label(self, phone: str, label: str) -> None:
        """Assign a label to an existing phone number.

        Args:
            phone: The phone number to label.
            label: The label string to assign.

        Raises:
            ValueError: If *phone* does not exist on the contact or the label
                is invalid.
        """
        phone_record = self.find_phone(phone)
        if phone_record is None:
            raise ValueError(f"Phone number '{phone}' does not exist")
        phone_record.label = Phone._normalize_label(label)

    def remove_phone_label(self, phone: str) -> None:
        """Remove the label from a phone number.

        Args:
            phone: The phone number whose label should be removed.

        Raises:
            ValueError: If *phone* does not exist or has no label.
        """
        phone_record = self.find_phone(phone)
        if phone_record is None:
            raise ValueError(f"Phone number '{phone}' does not exist")
        if phone_record.label is None:
            raise ValueError(f"Phone number '{phone}' does not have a label")
        phone_record.label = None

    def find_phone(self, phone: str) -> Phone | None:
        """Find a phone number object by its value.

        Args:
            phone: The phone number string to look for.

        Returns:
            The matching :class:`Phone` object, or ``None`` if not found.
        """
        for p in self.phones:
            if p.value == phone:
                return p

    def _find_phone_index(self, phone: str) -> int | None:
        """Return the list index of a phone number.

        Args:
            phone: The phone number string to search for.

        Returns:
            The zero-based index of the phone in :attr:`phones`, or ``None``
            if not found.
        """
        for i, p in enumerate(self.phones):
            if p.value == phone:
                return i

    def add_birthday(self, birthday: str) -> None:
        """Set or overwrite the contact's birthday.

        Args:
            birthday: Birthday string in ``DD.MM.YYYY`` format.

        Raises:
            ValueError: If the format is invalid.
        """
        self.birthday = Birthday(birthday)

    def remove_birthday(self) -> None:
        """Clear the contact's birthday.

        Raises:
            ValueError: If no birthday is currently set.
        """
        if self.birthday is None:
            raise ValueError("Birthday is not set")
        self.birthday = None

    def add_email(self, email: str) -> None:
        """Add an email address to the contact.

        Args:
            email: The email address to add.

        Raises:
            ValueError: If *email* already exists or is invalid.
        """
        email_idx = self._find_email_index(email)
        if email_idx is not None:
            raise ValueError(f"Email '{email}' already exists")
        self.emails.append(Email(email))

    def remove_email(self, email: str) -> None:
        """Remove an email address from the contact.

        Args:
            email: The email address to remove.

        Raises:
            ValueError: If *email* does not exist on the contact.
        """
        email_idx = self._find_email_index(email)
        if email_idx is None:
            raise ValueError(f"Email '{email}' does not exist")
        del self.emails[email_idx]

    def edit_email(self, old_email: str, new_email: str) -> None:
        """Replace an existing email address with a new one.

        Args:
            old_email: The email address to replace.
            new_email: The replacement email address.

        Raises:
            ValueError: If *old_email* equals *new_email*, *old_email* does not
                exist, or *new_email* already exists on the contact.
        """
        if old_email == new_email:
            raise ValueError("New email must be different from the current one")
        email_idx = self._find_email_index(old_email)
        if email_idx is None:
            raise ValueError(f"Email '{old_email}' does not exist")
        existing_email_idx = self._find_email_index(new_email)
        if existing_email_idx is not None:
            raise ValueError(f"Email '{new_email}' already exists")
        self.emails[email_idx] = Email(new_email, label=self.emails[email_idx].label)

    def add_email_label(self, email: str, label: str) -> None:
        """Assign a label to an existing email address.

        Args:
            email: The email address to label.
            label: The label string to assign.

        Raises:
            ValueError: If *email* does not exist or the label is invalid.
        """
        email_record = self.find_email(email)
        if email_record is None:
            raise ValueError(f"Email '{email}' does not exist")
        email_record.label = Email._normalize_label(label)

    def remove_email_label(self, email: str) -> None:
        """Remove the label from an email address.

        Args:
            email: The email address whose label should be removed.

        Raises:
            ValueError: If *email* does not exist or has no label.
        """
        email_record = self.find_email(email)
        if email_record is None:
            raise ValueError(f"Email '{email}' does not exist")
        if email_record.label is None:
            raise ValueError(f"Email '{email}' does not have a label")
        email_record.label = None

    def find_email(self, email: str) -> Email | None:
        """Find an email address object by its value.

        Args:
            email: The email string to search for.

        Returns:
            The matching :class:`Email` object, or ``None`` if not found.
        """
        for e in self.emails:
            if e.value == email:
                return e

    def _find_email_index(self, email: str) -> int | None:
        """Return the list index of an email address.

        Args:
            email: The email string to search for.

        Returns:
            The zero-based index in :attr:`emails`, or ``None`` if not found.
        """
        for i, e in enumerate(self.emails):
            if e.value == email:
                return i

    def add_address(self, address: str) -> None:
        """Add a postal address to the contact.

        Args:
            address: The address string to add.

        Raises:
            ValueError: If *address* already exists or is invalid.
        """
        address_idx = self._find_address_index(address)
        if address_idx is not None:
            raise ValueError(f"Address '{address}' already exists")
        self.addresses.append(Address(address))

    def remove_address(self, address: str) -> None:
        """Remove a postal address from the contact.

        Args:
            address: The address string to remove.

        Raises:
            ValueError: If *address* does not exist on the contact.
        """
        address_idx = self._find_address_index(address)
        if address_idx is None:
            raise ValueError(f"Address '{address}' does not exist")
        del self.addresses[address_idx]

    def edit_address(self, old_address: str, new_address: str) -> None:
        """Replace an existing address with a new one.

        Args:
            old_address: The address to replace.
            new_address: The replacement address.

        Raises:
            ValueError: If *old_address* equals *new_address*, *old_address* does
                not exist, or *new_address* already exists on the contact.
        """
        if old_address == new_address:
            raise ValueError("New address must be different from the current one")
        address_idx = self._find_address_index(old_address)
        if address_idx is None:
            raise ValueError(f"Address '{old_address}' does not exist")
        existing_address_idx = self._find_address_index(new_address)
        if existing_address_idx is not None:
            raise ValueError(f"Address '{new_address}' already exists")
        self.addresses[address_idx] = Address(
            new_address, label=self.addresses[address_idx].label
        )

    def add_address_label(self, address: str, label: str) -> None:
        """Assign a label to an existing address.

        Args:
            address: The address to label.
            label: The label string to assign.

        Raises:
            ValueError: If *address* does not exist or the label is invalid.
        """
        address_record = self.find_address(address)
        if address_record is None:
            raise ValueError(f"Address '{address}' does not exist")
        address_record.label = Address._normalize_label(label)

    def remove_address_label(self, address: str) -> None:
        """Remove the label from an address.

        Args:
            address: The address whose label should be removed.

        Raises:
            ValueError: If *address* does not exist or has no label.
        """
        address_record = self.find_address(address)
        if address_record is None:
            raise ValueError(f"Address '{address}' does not exist")
        if address_record.label is None:
            raise ValueError(f"Address '{address}' does not have a label")
        address_record.label = None

    def find_address(self, address: str) -> Address | None:
        """Find an address object by its value.

        Args:
            address: The address string to search for.

        Returns:
            The matching :class:`Address` object, or ``None`` if not found.
        """
        for a in self.addresses:
            if a.value == address:
                return a

    def _find_address_index(self, address: str) -> int | None:
        """Return the list index of an address.

        Args:
            address: The address string to search for.

        Returns:
            The zero-based index in :attr:`addresses`, or ``None`` if not found.
        """
        for i, a in enumerate(self.addresses):
            if a.value == address:
                return i

    def mark_favorite(self) -> None:
        """Mark this contact as a favorite."""
        self.is_favorite = True

    def unmark_favorite(self) -> None:
        """Remove this contact's favorite status."""
        self.is_favorite = False

    def __str__(self) -> str:
        """Return a single-line summary of the contact.

        Returns:
            A formatted string with the name (prefixed with ``* `` if favorite),
            phones, emails, addresses, and birthday.
        """
        return (
            f"{'* ' if self.is_favorite else ''}{self.name}: "
            f"phones: {', '.join(str(p) for p in self.phones) if self.phones else '-'}; "
            f"emails: {', '.join(str(e) for e in self.emails) if self.emails else '-'}; "
            f"addresses: {', '.join(str(a) for a in self.addresses) if self.addresses else '-'}; "
            f"birthday: {self.birthday if self.birthday else '-'}"
        )


class ContactsBook(UserDict):
    def add_record(self, record: ContactRecord) -> None:
        """Add a contact record to the book.

        Args:
            record: The :class:`ContactRecord` to store, keyed by its name value.
        """
        self.data[record.name.value] = record

    def find(self, name: str) -> ContactRecord | None:
        """Look up a contact by name.

        Args:
            name: The contact name to search for.

        Returns:
            The :class:`ContactRecord` if found, otherwise ``None``.
        """
        return self.data.get(name)

    def delete(self, name: str) -> None:
        """Delete a contact record by name.

        Args:
            name: The name of the contact to remove.

        Raises:
            KeyError: If no contact with *name* exists in the book.
        """
        del self.data[name]

    @property
    def birthdays_count(self) -> int:
        """Return the number of contacts that have a birthday set.

        Returns:
            Count of contacts where ``birthday`` is not ``None``.
        """
        return sum(1 for record in self.data.values() if record.birthday)

    def get_upcoming_birthdays(self, days) -> list[dict]:
        """Return contacts whose birthdays fall within the next *days* days.

        Birthdays that land on a weekend are shifted to the following Monday
        for the congratulation date.

        Args:
            days: Look-ahead window in days (inclusive).

        Returns:
            A list of dicts, each containing ``"name"``, ``"birthday"`` (as a
            formatted string), and ``"congratulation_date"`` (``YYYY.MM.DD``).
        """
        current_date = date.today()
        upcoming_birthdays: list[dict] = []

        for record in self.data.values():
            if record.birthday is None:
                continue

            current_year_birthday = date(
                year=current_date.year,
                month=record.birthday.value.month,
                day=record.birthday.value.day,
            )

            if current_year_birthday >= current_date:
                next_birthday = current_year_birthday
            else:
                next_birthday = date(
                    year=current_date.year + 1,
                    month=record.birthday.value.month,
                    day=record.birthday.value.day,
                )

            dates_diff = next_birthday - current_date
            if dates_diff.days > days:
                continue

            congratulation_date = next_birthday
            if congratulation_date.isoweekday() == 6:  # Saturday -> Monday
                congratulation_date += timedelta(days=2)
            elif congratulation_date.isoweekday() == 7:  # Sunday -> Monday
                congratulation_date += timedelta(days=1)

            upcoming_birthdays.append(
                {
                    "name": record.name,
                    "birthday": str(record.birthday),
                    "congratulation_date": congratulation_date.strftime("%Y.%m.%d"),
                }
            )

        return upcoming_birthdays

    @classmethod
    def from_file(cls, path: str | Path) -> Self:
        """Load a :class:`ContactsBook` from a pickle file.

        Args:
            path: Path to the pickle file to read.

        Returns:
            The deserialised :class:`ContactsBook`, or a new empty instance if
            the file does not exist.
        """
        try:
            with open(path, "rb") as f:
                return pickle.load(f)
        except FileNotFoundError:
            return cls()

    def save(self, path: str | Path) -> None:
        """Serialise and persist the contacts book to a pickle file.

        Args:
            path: Destination file path. Parent directories are created
                automatically if they do not exist.
        """
        path = Path(path)
        ensure_file_dir_exists(path)
        with path.open("wb") as f:
            pickle.dump(self, f)
