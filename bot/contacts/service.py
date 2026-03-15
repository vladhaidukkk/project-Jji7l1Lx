from typing import Literal, NamedTuple, Optional

from bot.utils.search_utils import fuzzy_search, sort_and_limit_matches
from rapidfuzz.distance import ScoreAlignment

from .errors import ContactAlreadyExistsError, ContactNotFoundError
from .models import ContactRecord, ContactsBook, Name


class SearchResultItemForContacts(NamedTuple):
    contact: ContactRecord
    score_alignment: Optional[ScoreAlignment]

class ContactsService:
    def __init__(self, contacts: ContactsBook) -> None:
        """Initialise the service with a contacts book.

        Args:
            contacts: The :class:`ContactsBook` instance this service operates on.
        """
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
        """Create a new contact, optionally with initial details.

        Args:
            name: The contact's name.
            phone: An optional phone number to attach immediately.
            birthday: An optional birthday in ``DD.MM.YYYY`` format.
            email: An optional email address.
            address: An optional postal address.

        Raises:
            ContactAlreadyExistsError: If a contact named *name* already exists.
            ValueError: If any of the optional field values are invalid.
        """
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
        """Add a phone number to an existing contact.

        Args:
            name: The contact's name.
            phone: The phone number to add.

        Raises:
            ContactNotFoundError: If no contact named *name* exists.
            ValueError: If *phone* is invalid or already present.
        """
        contact = self.__contacts.find(name)
        if not contact:
            raise ContactNotFoundError(f"Contact '{name}' does not exist.")
        contact.add_phone(phone)

    def delete_phone(self, name: str, *, phone: str) -> None:
        """Remove a phone number from a contact.

        Args:
            name: The contact's name.
            phone: The phone number to remove.

        Raises:
            ContactNotFoundError: If no contact named *name* exists.
            ValueError: If *phone* does not exist on the contact.
        """
        contact = self.__contacts.find(name)
        if not contact:
            raise ContactNotFoundError(f"Contact '{name}' does not exist.")
        contact.remove_phone(phone)

    def add_phone_label(self, name: str, *, phone: str, label: str) -> None:
        """Assign a label to one of a contact's phone numbers.

        Args:
            name: The contact's name.
            phone: The phone number to label.
            label: The label to assign.

        Raises:
            ContactNotFoundError: If no contact named *name* exists.
            ValueError: If *phone* does not exist or *label* is invalid.
        """
        contact = self.__contacts.find(name)
        if not contact:
            raise ContactNotFoundError(f"Contact '{name}' does not exist.")
        contact.add_phone_label(phone, label)

    def delete_phone_label(self, name: str, *, phone: str) -> None:
        """Remove the label from one of a contact's phone numbers.

        Args:
            name: The contact's name.
            phone: The phone number whose label should be removed.

        Raises:
            ContactNotFoundError: If no contact named *name* exists.
            ValueError: If *phone* does not exist or has no label.
        """
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
        """Set or update a contact's birthday.

        Args:
            name: The contact's name.
            birthday: The birthday string in ``DD.MM.YYYY`` format.

        Returns:
            ``"added"`` if the contact had no previous birthday, or
            ``"updated"`` if an existing one was overwritten.

        Raises:
            ContactNotFoundError: If no contact named *name* exists.
            ValueError: If *birthday* has an invalid format.
        """
        contact = self.__contacts.find(name)
        if not contact:
            raise ContactNotFoundError(f"Contact '{name}' does not exist.")
        had_birthday = contact.birthday is not None
        contact.add_birthday(birthday)
        return "updated" if had_birthday else "added"

    def delete_birthday(self, name: str) -> None:
        """Remove a contact's birthday.

        Args:
            name: The contact's name.

        Raises:
            ContactNotFoundError: If no contact named *name* exists.
            ValueError: If the contact has no birthday set.
        """
        contact = self.__contacts.find(name)
        if not contact:
            raise ContactNotFoundError(f"Contact '{name}' does not exist.")
        contact.remove_birthday()

    def add_email(self, name: str, *, email: str) -> None:
        """Add an email address to a contact.

        Args:
            name: The contact's name.
            email: The email address to add.

        Raises:
            ContactNotFoundError: If no contact named *name* exists.
            ValueError: If *email* is invalid or already present.
        """
        contact = self.__contacts.find(name)
        if not contact:
            raise ContactNotFoundError(f"Contact '{name}' does not exist.")
        contact.add_email(email)

    def delete_email(self, name: str, *, email: str) -> None:
        """Remove an email address from a contact.

        Args:
            name: The contact's name.
            email: The email address to remove.

        Raises:
            ContactNotFoundError: If no contact named *name* exists.
            ValueError: If *email* does not exist on the contact.
        """
        contact = self.__contacts.find(name)
        if not contact:
            raise ContactNotFoundError(f"Contact '{name}' does not exist.")
        contact.remove_email(email)

    def change_email(self, name: str, *, old_email: str, new_email: str) -> None:
        """Replace one of a contact's email addresses.

        Args:
            name: The contact's name.
            old_email: The email address to replace.
            new_email: The replacement email address.

        Raises:
            ContactNotFoundError: If no contact named *name* exists.
            ValueError: If *old_email* does not exist or *new_email* is invalid.
        """
        contact = self.__contacts.find(name)
        if not contact:
            raise ContactNotFoundError(f"Contact '{name}' does not exist.")
        contact.edit_email(old_email, new_email)

    def add_email_label(self, name: str, *, email: str, label: str) -> None:
        """Assign a label to one of a contact's email addresses.

        Args:
            name: The contact's name.
            email: The email address to label.
            label: The label to assign.

        Raises:
            ContactNotFoundError: If no contact named *name* exists.
            ValueError: If *email* does not exist or *label* is invalid.
        """
        contact = self.__contacts.find(name)
        if not contact:
            raise ContactNotFoundError(f"Contact '{name}' does not exist.")
        contact.add_email_label(email, label)

    def delete_email_label(self, name: str, *, email: str) -> None:
        """Remove the label from one of a contact's email addresses.

        Args:
            name: The contact's name.
            email: The email address whose label should be removed.

        Raises:
            ContactNotFoundError: If no contact named *name* exists.
            ValueError: If *email* does not exist or has no label.
        """
        contact = self.__contacts.find(name)
        if not contact:
            raise ContactNotFoundError(f"Contact '{name}' does not exist.")
        contact.remove_email_label(email)

    def add_address(self, name: str, *, address: str) -> None:
        """Add a postal address to a contact.

        Args:
            name: The contact's name.
            address: The address string to add.

        Raises:
            ContactNotFoundError: If no contact named *name* exists.
            ValueError: If *address* is invalid or already present.
        """
        contact = self.__contacts.find(name)
        if not contact:
            raise ContactNotFoundError(f"Contact '{name}' does not exist.")
        contact.add_address(address)

    def delete_address(self, name: str, *, address: str) -> None:
        """Remove a postal address from a contact.

        Args:
            name: The contact's name.
            address: The address string to remove.

        Raises:
            ContactNotFoundError: If no contact named *name* exists.
            ValueError: If *address* does not exist on the contact.
        """
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
        """Replace one of a contact's addresses.

        Args:
            name: The contact's name.
            old_address: The address to replace.
            new_address: The replacement address.

        Raises:
            ContactNotFoundError: If no contact named *name* exists.
            ValueError: If *old_address* does not exist or *new_address* is
                invalid.
        """
        contact = self.__contacts.find(name)
        if not contact:
            raise ContactNotFoundError(f"Contact '{name}' does not exist.")
        contact.edit_address(old_address, new_address)

    def add_address_label(self, name: str, *, address: str, label: str) -> None:
        """Assign a label to one of a contact's addresses.

        Args:
            name: The contact's name.
            address: The address to label.
            label: The label to assign.

        Raises:
            ContactNotFoundError: If no contact named *name* exists.
            ValueError: If *address* does not exist or *label* is invalid.
        """
        contact = self.__contacts.find(name)
        if not contact:
            raise ContactNotFoundError(f"Contact '{name}' does not exist.")
        contact.add_address_label(address, label)

    def delete_address_label(self, name: str, *, address: str) -> None:
        """Remove the label from one of a contact's addresses.

        Args:
            name: The contact's name.
            address: The address whose label should be removed.

        Raises:
            ContactNotFoundError: If no contact named *name* exists.
            ValueError: If *address* does not exist or has no label.
        """
        contact = self.__contacts.find(name)
        if not contact:
            raise ContactNotFoundError(f"Contact '{name}' does not exist.")
        contact.remove_address_label(address)

    def get_contact(self, name: str) -> ContactRecord | None:
        """Retrieve a contact record by name.

        Args:
            name: The contact name to look up.

        Returns:
            The :class:`ContactRecord` if found, otherwise ``None``.
        """
        return self.__contacts.find(name)

    def mark_favorite(self, name: str) -> None:
        """Mark a contact as a favorite.

        Args:
            name: The contact's name.

        Raises:
            ContactNotFoundError: If no contact named *name* exists.
        """
        contact = self.__contacts.find(name)
        if not contact:
            raise ContactNotFoundError(f"Contact '{name}' does not exist.")
        contact.mark_favorite()

    def unmark_favorite(self, name: str) -> None:
        """Remove a contact's favorite status.

        Args:
            name: The contact's name.

        Raises:
            ContactNotFoundError: If no contact named *name* exists.
        """
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
        """Update one or more fields of an existing contact.

        Args:
            name: The contact's name.
            phone: A ``(old_phone, new_phone)`` tuple to replace a phone number.
            birthday: A new birthday string in ``DD.MM.YYYY`` format.
            email: A ``(old_email, new_email)`` tuple to replace an email.
            address: A ``(old_address, new_address)`` tuple to replace an address.

        Raises:
            ContactNotFoundError: If no contact named *name* exists.
            ValueError: If any supplied field value is invalid.
        """
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
        """Permanently delete a contact.

        Args:
            name: The name of the contact to delete.

        Raises:
            ContactNotFoundError: If no contact named *name* exists.
        """
        contact = self.__contacts.find(name)
        if not contact:
            raise ContactNotFoundError(f"Contact '{name}' does not exist.")
        self.__contacts.delete(name)

    def rename_contact(
        self,
        old_name: str,
        new_name: str,
    ) -> Literal["renamed", "skipped"]:
        """Rename a contact.

        Args:
            old_name: The current name of the contact.
            new_name: The desired new name.

        Returns:
            ``"renamed"`` if the contact was renamed, or ``"skipped"`` if
            *old_name* and *new_name* are identical.

        Raises:
            ContactNotFoundError: If no contact named *old_name* exists.
            ContactAlreadyExistsError: If a contact named *new_name* already
                exists.
        """
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
        """Search contacts using fuzzy matching on a specific field.

        Args:
            query: The search string (case-insensitive).
            field: The field to search; one of ``"name"``, ``"phone"``,
                ``"email"``, or ``"address"``.
            score_cutoff: Minimum fuzzy-match score (0–100) for a result to be
                included. Defaults to ``50.0``.
            limit: Maximum number of results to return. Defaults to ``5``.

        Returns:
            A list of :class:`SearchResultItemForContacts` tuples sorted by
            descending match score, capped at *limit* entries.
        """
        query = query.lower()
        matches: list[SearchResultItemForContacts] = []

        for contact in self.__contacts.data.values():
            # Match against name (case-insensitive)
            lowercased_field = field.lower()

            match lowercased_field:
                case "name":
                    field_value = contact.name
                case "address":
                    field_value = contact.addresses
                case "email":
                    field_value = contact.emails
                case "phone":
                    field_value = contact.phones
                case _:
                    field_value = None

            name_score, field_res = fuzzy_search(query, field_value)

            if name_score >= score_cutoff:
                matches.append(SearchResultItemForContacts(contact, field_res))

        return sort_and_limit_matches(matches, limit, sort_key=lambda item: item.score_alignment.score)
