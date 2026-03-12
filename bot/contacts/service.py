from typing import Literal

from .errors import ContactAlreadyExistsError, ContactNotFoundError
from .models import ContactRecord, ContactsBook, Name


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

    def add_contact(
        self,
        name: str,
        *,
        phone: str | None = None,
        birthday: str | None = None,
        email: str | None = None,
        address: str | None = None,
    ) -> str:
        contact = self.__contacts.find(name)
        if not contact:
            self.create_contact(
                name,
                phone=phone,
                birthday=birthday,
                email=email,
                address=address,
            )
            return "added"

        updated = []
        if not contact.phones and phone:
            self.add_phone(name, phone=phone)
            updated.append("phone")
        if not contact.birthday and birthday:
            self.add_birthday(name, birthday=birthday)
            updated.append("birthday")
        if not contact.email and email:
            self.add_email(name, email=email)
            updated.append("email")
        if not contact.address and address:
            self.add_address(name, address=address)
            updated.append("address")

        if updated:
            return f"updated:{'|'.join(updated)}"

        raise ContactAlreadyExistsError(f"Contact '{name}' aready exists")

    def add_phone(self, name: str, *, phone: str) -> None:
        contact = self.__contacts.find(name)
        if not contact:
            raise ContactNotFoundError(f"Contact '{name}' does not exist.")

        contact.add_phone(phone)

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

    def add_email(
        self,
        name: str,
        *,
        email: str,
    ) -> Literal["added", "updated"]:
        contact = self.__contacts.find(name)
        if not contact:
            raise ContactNotFoundError(f"Contact '{name}' does not exist.")

        had_email = contact.email is not None
        contact.add_email(email)
        return "updated" if had_email else "added"

    def add_address(
        self,
        name: str,
        *,
        address: str,
    ) -> Literal["added", "updated"]:
        contact = self.__contacts.find(name)
        if not contact:
            raise ContactNotFoundError(f"Contact '{name}' does not exist.")

        had_address = contact.address is not None
        contact.add_address(address)
        return "updated" if had_address else "added"

    def get_contact(self, name: str) -> ContactRecord | None:
        return self.__contacts.find(name)

    def update_contact(
        self,
        name: str,
        *,
        phone: tuple[str, str] | None = None,
        birthday: str | None = None,
        email: str | None = None,
        address: str | None = None,
    ) -> None:
        contact = self.__contacts.find(name)
        if not contact:
            raise ContactNotFoundError(f"Contact '{name}' does not exist.")

        if phone:
            contact.edit_phone(phone[0], phone[1])
        if birthday:
            contact.add_birthday(birthday)
        if email:
            contact.add_email(email)
        if address:
            contact.add_address(address)

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
