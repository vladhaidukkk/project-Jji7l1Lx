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
        value_stripped = value.strip()
        super().__init__(value_stripped)
        self.value = value_stripped

    @property
    def value(self) -> str:
        return self._value

    @value.setter
    def value(self, value: str) -> None:
        if not value:
            raise ValueError("Note name cannot be empty")
        self._value = value


class Phone(Field):
    def __init__(self, value: str, label: str | None = None) -> None:
        value_stripped = value.strip()
        super().__init__(value_stripped)
        self.value = value_stripped
        self.label = self._normalize_label(label) if label else None

    @property
    def value(self) -> str:
        return self._value

    @value.setter
    def value(self, value: str) -> None:
        # Phone number validation
        if not value:
            raise ValueError("Phone number cannot be empty")
        if len(value) != 10:
            raise ValueError("Phone number must be exactly 10 digits")
        if not value.isdigit():
            raise ValueError("Phone number must contain only digits")
        self._value = value
        self.label = self._normalize_label(label) if label else None

    @staticmethod
    def _normalize_label(label: str) -> str:
        label = label.strip()
        if not label:
            raise ValueError("Phone label cannot be empty")

        return label

    def __str__(self) -> str:
        return f"{self.value} ({self.label})" if self.label else self.value


class Birthday(Field):
    def __init__(self, value: str) -> None:
        value_stripped = value.strip()
        super().__init__(value_stripped)
        self.value = value_stripped
        try:
            value = datetime.strptime(value.strip(), "%d.%m.%Y")
            super().__init__(value)
        except ValueError:
            raise ValueError("Invalid birthday format. Use DD.MM.YYYY")

    def __str__(self) -> str:
        return self.value.strftime("%Y.%m.%d")

    @property
    def value(self) -> str:
        return self._value

    @value.setter
    def value(self, value: str) -> None:
        # Birthday validation
        try:
            value_parsed = datetime.strptime(value, "%d.%m.%Y")
            self._value = value_parsed
        except ValueError:
            raise ValueError("Invalid birthday format. Use DD.MM.YYYY")


class Email(Field):
    def __init__(self, value: str, label: str | None = None) -> None:
        # Email validation
        value = value.strip()
        if not value:
            raise ValueError("Email cannot be empty")
        if not EMAIL_PATTERN.fullmatch(value):
            raise ValueError("Invalid email format")

        super().__init__(value)
        self.label = self._normalize_label(label) if label else None

    @staticmethod
    def _normalize_label(label: str) -> str:
        label = label.strip()
        if not label:
            raise ValueError("Email label cannot be empty")

        return label

    def __str__(self) -> str:
        return f"{self.value} ({self.label})" if self.label else self.value


class Address(Field):
    def __init__(self, value: str, label: str | None = None) -> None:
        value_stripped = value.strip()
        super().__init__(value_stripped)
        self.value = value_stripped
        self.label = self._normalize_label(label) if label else None

    @property
    def value(self) -> str:
        return self._value

    @value.setter
    def value(self, value: str) -> None:
        # Address validation
        value = value.strip()
        if not value:
            raise ValueError("Address cannot be empty")
        self._value = value

    @staticmethod
    def _normalize_label(label: str) -> str:
        label = label.strip()
        if not label:
            raise ValueError("Address label cannot be empty")

        return label

    def __str__(self) -> str:
        return f"{self.value} ({self.label})" if self.label else self.value


class ContactRecord:
    def __init__(self, name: str) -> None:
        self.name = Name(name)
        self.phones: list[Phone] = []
        self.birthday: Birthday | None = None
        self.emails: list[Email] = []
        self.addresses: list[Address] = []
        self.is_favorite = False

    def add_phone(self, phone: str) -> None:
        phone_idx = self._find_phone_index(phone)
        if phone_idx is not None:
            raise ValueError(f"Phone number '{phone}' already exists")

        self.phones.append(Phone(phone))

    def remove_phone(self, phone: str) -> None:
        phone_idx = self._find_phone_index(phone)
        if phone_idx is None:
            raise ValueError(f"Phone number '{phone}' does not exist")

        del self.phones[phone_idx]

    def edit_phone(self, old_phone: str, new_phone: str) -> None:
        if old_phone == new_phone:
            raise ValueError("New phone number must be different from the current one")

        phone_idx = self._find_phone_index(old_phone)
        if phone_idx is None:
            raise ValueError(f"Phone number '{old_phone}' does not exist")

        existing_phone_idx = self._find_phone_index(new_phone)
        if existing_phone_idx is not None:
            raise ValueError(f"Phone number '{new_phone}' already exists")

        self.phones[phone_idx] = Phone(
            new_phone,
            label=self.phones[phone_idx].label,
        )

    def add_phone_label(self, phone: str, label: str) -> None:
        phone_record = self.find_phone(phone)
        if phone_record is None:
            raise ValueError(f"Phone number '{phone}' does not exist")

        phone_record.label = Phone._normalize_label(label)

    def remove_phone_label(self, phone: str) -> None:
        phone_record = self.find_phone(phone)
        if phone_record is None:
            raise ValueError(f"Phone number '{phone}' does not exist")

        if phone_record.label is None:
            raise ValueError(f"Phone number '{phone}' does not have a label")

        phone_record.label = None

    def find_phone(self, phone: str) -> Phone | None:
        for p in self.phones:
            if p.value == phone:
                return p

    def _find_phone_index(self, phone: str) -> int | None:
        for i, p in enumerate(self.phones):
            if p.value == phone:
                return i

    def add_birthday(self, birthday: str) -> None:
        self.birthday = Birthday(birthday)

    def remove_birthday(self) -> None:
        if self.birthday is None:
            raise ValueError("Birthday is not set")

        self.birthday = None

    def add_email(self, email: str) -> None:
        email_idx = self._find_email_index(email)
        if email_idx is not None:
            raise ValueError(f"Email '{email}' already exists")

        self.emails.append(Email(email))

    def remove_email(self, email: str) -> None:
        email_idx = self._find_email_index(email)
        if email_idx is None:
            raise ValueError(f"Email '{email}' does not exist")

        del self.emails[email_idx]

    def edit_email(self, old_email: str, new_email: str) -> None:
        if old_email == new_email:
            raise ValueError("New email must be different from the current one")

        email_idx = self._find_email_index(old_email)
        if email_idx is None:
            raise ValueError(f"Email '{old_email}' does not exist")

        existing_email_idx = self._find_email_index(new_email)
        if existing_email_idx is not None:
            raise ValueError(f"Email '{new_email}' already exists")

        self.emails[email_idx] = Email(
            new_email,
            label=self.emails[email_idx].label,
        )

    def add_email_label(self, email: str, label: str) -> None:
        email_record = self.find_email(email)
        if email_record is None:
            raise ValueError(f"Email '{email}' does not exist")

        email_record.label = Email._normalize_label(label)

    def remove_email_label(self, email: str) -> None:
        email_record = self.find_email(email)
        if email_record is None:
            raise ValueError(f"Email '{email}' does not exist")

        if email_record.label is None:
            raise ValueError(f"Email '{email}' does not have a label")

        email_record.label = None

    def find_email(self, email: str) -> Email | None:
        for e in self.emails:
            if e.value == email:
                return e

    def _find_email_index(self, email: str) -> int | None:
        for i, e in enumerate(self.emails):
            if e.value == email:
                return i

    def add_address(self, address: str) -> None:
        address_idx = self._find_address_index(address)
        if address_idx is not None:
            raise ValueError(f"Address '{address}' already exists")

        self.addresses.append(Address(address))

    def remove_address(self, address: str) -> None:
        address_idx = self._find_address_index(address)
        if address_idx is None:
            raise ValueError(f"Address '{address}' does not exist")

        del self.addresses[address_idx]

    def edit_address(self, old_address: str, new_address: str) -> None:
        if old_address == new_address:
            raise ValueError("New address must be different from the current one")

        address_idx = self._find_address_index(old_address)
        if address_idx is None:
            raise ValueError(f"Address '{old_address}' does not exist")

        existing_address_idx = self._find_address_index(new_address)
        if existing_address_idx is not None:
            raise ValueError(f"Address '{new_address}' already exists")

        self.addresses[address_idx] = Address(
            new_address,
            label=self.addresses[address_idx].label,
        )

    def add_address_label(self, address: str, label: str) -> None:
        address_record = self.find_address(address)
        if address_record is None:
            raise ValueError(f"Address '{address}' does not exist")

        address_record.label = Address._normalize_label(label)

    def remove_address_label(self, address: str) -> None:
        address_record = self.find_address(address)
        if address_record is None:
            raise ValueError(f"Address '{address}' does not exist")

        if address_record.label is None:
            raise ValueError(f"Address '{address}' does not have a label")

        address_record.label = None

    def find_address(self, address: str) -> Address | None:
        for a in self.addresses:
            if a.value == address:
                return a

    def _find_address_index(self, address: str) -> int | None:
        for i, a in enumerate(self.addresses):
            if a.value == address:
                return i

    def mark_favorite(self) -> None:
        self.is_favorite = True

    def unmark_favorite(self) -> None:
        self.is_favorite = False

    def __str__(self) -> str:
        return (
            f"{'* ' if self.is_favorite else ''}{self.name}: "
            f"phones: {', '.join(str(p) for p in self.phones) if self.phones else '-'}; "
            f"emails: {', '.join(str(e) for e in self.emails) if self.emails else '-'}; "
            f"addresses: {', '.join(str(a) for a in self.addresses) if self.addresses else '-'}; "
            f"birthday: {self.birthday if self.birthday else '-'}"
        )


class ContactsBook(UserDict):
    def add_record(self, record: ContactRecord) -> None:
        self.data[record.name.value] = record

    def find(self, name: str) -> ContactRecord | None:
        return self.data.get(name)

    def delete(self, name: str) -> None:
        del self.data[name]

    @property
    def birthdays_count(self) -> int:
        return sum(1 for record in self.data.values() if record.birthday)

    def get_upcoming_birthdays(self) -> list[dict]:
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
            if dates_diff.days > 7:
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
        try:
            with open(path, "rb") as f:
                return pickle.load(f)
        except FileNotFoundError:
            return cls()

    def save(self, path: str | Path) -> None:
        path = Path(path)
        ensure_file_dir_exists(path)
        with path.open("wb") as f:
            pickle.dump(self, f)
