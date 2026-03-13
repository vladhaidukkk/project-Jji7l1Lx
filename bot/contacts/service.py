from typing import Literal, Optional

from bot.utils.search_utils import fuzzy_search, sort_and_limit_matches
from rapidfuzz.distance import ScoreAlignment

from .errors import ContactAlreadyExistsError, ContactNotFoundError
from .models import ContactRecord, ContactsBook, Name

SearchResultItemForContacts = tuple[ContactRecord, Optional[ScoreAlignment]]

class ContactsService:
    def __init__(self, contacts: ContactsBook) -> None:
        self.__contacts = contacts

    def create_contact(
        self,
        name: str,
        *,
        phone: str | None = None,
        birthday: str | None = None,
        email: str | None = None,
        address: str | None = None,
    ) -> None:
        contact = self.__contacts.find(name)
        if contact:
            raise ContactAlreadyExistsError(f"Contact '{name}' aready exists.")

        contact = ContactRecord(name)
        if phone:
            contact.add_phone(phone)
        if birthday:
            contact.add_birthday(birthday)
        if email:
            contact.add_email(email)
        if address:
            contact.add_address(address)
        self.__contacts.add_record(contact)

    def add_phone(self, name: str, *, phone: str) -> None:
        contact = self.__contacts.find(name)
        if not contact:
            raise ContactNotFoundError(f"Contact '{name}' does not exist.")

        contact.add_phone(phone)

    def delete_phone(self, name: str, *, phone: str) -> None:
        contact = self.__contacts.find(name)
        if not contact:
            raise ContactNotFoundError(f"Contact '{name}' does not exist.")

        contact.remove_phone(phone)

    def add_phone_label(self, name: str, *, phone: str, label: str) -> None:
        contact = self.__contacts.find(name)
        if not contact:
            raise ContactNotFoundError(f"Contact '{name}' does not exist.")

        contact.add_phone_label(phone, label)

    def delete_phone_label(self, name: str, *, phone: str) -> None:
        contact = self.__contacts.find(name)
        if not contact:
            raise ContactNotFoundError(f"Contact '{name}' does not exist.")

        contact.remove_phone_label(phone)

    def add_birthday(
        self,
        name: str,
        *,
        birthday: str,
    ) -> Literal["added", "updated"]:
        contact = self.__contacts.find(name)
        if not contact:
            raise ContactNotFoundError(f"Contact '{name}' does not exist.")

        had_birthday = contact.birthday is not None
        contact.add_birthday(birthday)
        return "updated" if had_birthday else "added"

    def delete_birthday(self, name: str) -> None:
        contact = self.__contacts.find(name)
        if not contact:
            raise ContactNotFoundError(f"Contact '{name}' does not exist.")

        contact.remove_birthday()

    def add_email(self, name: str, *, email: str) -> None:
        contact = self.__contacts.find(name)
        if not contact:
            raise ContactNotFoundError(f"Contact '{name}' does not exist.")

        contact.add_email(email)

    def delete_email(self, name: str, *, email: str) -> None:
        contact = self.__contacts.find(name)
        if not contact:
            raise ContactNotFoundError(f"Contact '{name}' does not exist.")

        contact.remove_email(email)

    def change_email(self, name: str, *, old_email: str, new_email: str) -> None:
        contact = self.__contacts.find(name)
        if not contact:
            raise ContactNotFoundError(f"Contact '{name}' does not exist.")

        contact.edit_email(old_email, new_email)

    def add_email_label(self, name: str, *, email: str, label: str) -> None:
        contact = self.__contacts.find(name)
        if not contact:
            raise ContactNotFoundError(f"Contact '{name}' does not exist.")

        contact.add_email_label(email, label)

    def delete_email_label(self, name: str, *, email: str) -> None:
        contact = self.__contacts.find(name)
        if not contact:
            raise ContactNotFoundError(f"Contact '{name}' does not exist.")

        contact.remove_email_label(email)

    def add_address(self, name: str, *, address: str) -> None:
        contact = self.__contacts.find(name)
        if not contact:
            raise ContactNotFoundError(f"Contact '{name}' does not exist.")

        contact.add_address(address)

    def delete_address(self, name: str, *, address: str) -> None:
        contact = self.__contacts.find(name)
        if not contact:
            raise ContactNotFoundError(f"Contact '{name}' does not exist.")

        contact.remove_address(address)

    def change_address(
        self,
        name: str,
        *,
        old_address: str,
        new_address: str,
    ) -> None:
        contact = self.__contacts.find(name)
        if not contact:
            raise ContactNotFoundError(f"Contact '{name}' does not exist.")

        contact.edit_address(old_address, new_address)

    def add_address_label(self, name: str, *, address: str, label: str) -> None:
        contact = self.__contacts.find(name)
        if not contact:
            raise ContactNotFoundError(f"Contact '{name}' does not exist.")

        contact.add_address_label(address, label)

    def delete_address_label(self, name: str, *, address: str) -> None:
        contact = self.__contacts.find(name)
        if not contact:
            raise ContactNotFoundError(f"Contact '{name}' does not exist.")

        contact.remove_address_label(address)

    def get_contact(self, name: str) -> ContactRecord | None:
        return self.__contacts.find(name)

    def mark_favorite(self, name: str) -> None:
        contact = self.__contacts.find(name)
        if not contact:
            raise ContactNotFoundError(f"Contact '{name}' does not exist.")

        contact.mark_favorite()

    def unmark_favorite(self, name: str) -> None:
        contact = self.__contacts.find(name)
        if not contact:
            raise ContactNotFoundError(f"Contact '{name}' does not exist.")

        contact.unmark_favorite()

    def update_contact(
        self,
        name: str,
        *,
        phone: tuple[str, str] | None = None,
        birthday: str | None = None,
        email: tuple[str, str] | None = None,
        address: tuple[str, str] | None = None,
    ) -> None:
        contact = self.__contacts.find(name)
        if not contact:
            raise ContactNotFoundError(f"Contact '{name}' does not exist.")

        if phone:
            contact.edit_phone(phone[0], phone[1])
        if birthday:
            contact.add_birthday(birthday)
        if email:
            contact.edit_email(email[0], email[1])
        if address:
            contact.edit_address(address[0], address[1])

    def delete_contact(self, name: str) -> None:
        contact = self.__contacts.find(name)
        if not contact:
            raise ContactNotFoundError(f"Contact '{name}' does not exist.")

        self.__contacts.delete(name)

    def rename_contact(
        self,
        old_name: str,
        new_name: str,
    ) -> Literal["renamed", "skipped"]:
        if old_name == new_name:
            return "skipped"

        contact = self.__contacts.find(old_name)
        if not contact:
            raise ContactNotFoundError(f"Contact '{old_name}' does not exist.")

        if self.__contacts.find(new_name):
            raise ContactAlreadyExistsError(f"Contact '{new_name}' already exists.")

        new_name = Name(new_name)
        self.__contacts.delete(old_name)
        contact.name = new_name
        self.__contacts.add_record(contact)
        return "renamed"

    def search_contacts_by_field(
        self,
        query: str,
        field: str,
        *,
        score_cutoff: float = 50.0,
        limit: int = 5,
    ) -> list[SearchResultItemForContacts]:
        query = query.lower()

        matches: list[SearchResultItemForContacts] = []

        for contact in self.__contacts.data.values():
            # Match against name (case-insensitive)
            lowercased_field = field.lower()

            match lowercased_field:
                case "name":
                    lowercased_field = contact.name
                case "address":
                    lowercased_field = contact.address
                case "email":
                    lowercased_field = contact.email
                case "phone":
                    lowercased_field = contact.phone
                case _:
                    lowercased_field = None

            name_score, field_res = fuzzy_search(query, lowercased_field)

            if name_score >= score_cutoff:
                matches.append((contact, field_res))

            return sort_and_limit_matches(matches, limit)
