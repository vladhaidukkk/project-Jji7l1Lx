from rich.text import Text

from bot.commands import CommandArgs, CommandContext, CommandsRegistry
from bot.console import console
from bot.contacts import ContactAlreadyExistsError, ContactNotFoundError
from bot.notes import NoteAlreadyExistsError, NoteNotFoundError
from bot.notes.editor import open_editor

bot_commands = CommandsRegistry()


@bot_commands.register(
    "hi",
    "hello",
    description="Say hi! A quick way to check if I'm awake and ready to help.",
)
def say_hello() -> None:
    print("How can I help you?")


@bot_commands.register(
    "help",
    "commands",
    description="Show detailed descriptions of available assistant commands.",
)
def show_commands() -> None:
    for command in bot_commands.get_primary_commands():
        console.print(command)


# ================================================
# Commands for contacts management
# ================================================


@bot_commands.register(
    "add",
    args=["contact name"],
    optional_args=["phone number", "email", "address", "birthday"],
    description=(
        "Create a new contact and optionally attach the first phone number, email, "
        "address, and birthday."
    ),
)
def add_contact(args: CommandArgs, context: CommandContext) -> None:
    name, phone, email, address, birthday = args
    contacts_service = context["contacts_service"]

    try:
        contacts_service.create_contact(
            name,
            phone=phone,
            email=email,
            address=address,
            birthday=birthday,
        )
        print("Contact added.")
    except ContactAlreadyExistsError:
        print("Contact already exists.")


@bot_commands.register(
    "rename-contact",
    args=["old contact name", "new contact name"],
    description="Rename an existing contact.",
)
def rename_contact(args: CommandArgs, context: CommandContext) -> None:
    old_name, new_name = args
    contacts_service = context["contacts_service"]

    try:
        match contacts_service.rename_contact(old_name, new_name):
            case "renamed":
                print(f"Contact '{old_name}' renamed to '{new_name}'.")
            case "skipped":
                print(f"Contact name is already '{new_name}'.")
    except ContactNotFoundError:
        print("Contact doesn't exist.")
    except ContactAlreadyExistsError:
        print("Contact with new name already exists.")


@bot_commands.register(
    "contacts",
    description="Show all saved contacts with their stored details.",
)
def list_contacts(context: CommandContext) -> None:
    contacts = context["contacts"]
    if not contacts:
        print("No contacts.")
        return

    print("\n".join(str(contact) for contact in contacts.values()))


@bot_commands.register(
    "favs",
    description="Show only contacts marked as favorites.",
)
def list_favorite_contacts(context: CommandContext) -> None:
    contacts = context["contacts"]
    if not contacts:
        print("No contacts.")
        return

    favorite_contacts = [c for c in contacts.values() if c.is_favorite]
    if not favorite_contacts:
        print("No favorite contacts.")
        return

    print("\n".join(str(contact) for contact in favorite_contacts))


@bot_commands.register(
    "fav",
    args=["contact name"],
    description="Mark a contact as favorite.",
)
def favorite_contact(args: CommandArgs, context: CommandContext) -> None:
    name = args[0]
    contacts_service = context["contacts_service"]

    try:
        contacts_service.mark_favorite(name)
        print(f"Contact '{name}' added to favorites.")
    except ContactNotFoundError:
        print("Contact doesn't exist.")


@bot_commands.register(
    "unfav",
    args=["contact name"],
    description="Remove a contact from favorites.",
)
def unfavorite_contact(args: CommandArgs, context: CommandContext) -> None:
    name = args[0]
    contacts_service = context["contacts_service"]

    try:
        contacts_service.unmark_favorite(name)
        print(f"Contact '{name}' removed from favorites.")
    except ContactNotFoundError:
        print("Contact doesn't exist.")


@bot_commands.register(
    "rm-contact",
    args=["contact name"],
    description="Delete a contact entirely.",
)
def delete_contact(args: CommandArgs, context: CommandContext) -> None:
    name = args[0]
    contacts_service = context["contacts_service"]

    try:
        contacts_service.delete_contact(name)
        print(f"Contact '{name}' deleted.")
    except ContactNotFoundError:
        print("Contact doesn't exist.")


# ------------------------------------------------
# Commands for contact phones management
# ------------------------------------------------


@bot_commands.register(
    "add-phone",
    args=["contact name", "phone number"],
    description="Add another phone number to an existing contact.",
)
def add_phone(args: CommandArgs, context: CommandContext) -> None:
    name, phone = args
    contacts_service = context["contacts_service"]

    try:
        contacts_service.add_phone(name, phone=phone)
        print("Phone number added.")
    except ContactNotFoundError:
        print("Contact doesn't exist.")


@bot_commands.register(
    "phones",
    args=["contact name"],
    description="List all phone numbers saved for a contact.",
)
def list_phones(args: CommandArgs, context: CommandContext) -> None:
    name = args[0]
    contacts_service = context["contacts_service"]

    contact = contacts_service.get_contact(name)
    if not contact:
        print("Contact doesn't exist.")
        return

    if not contact.phones:
        print("This contact doesn't have a phone number.")
        return

    print("\n".join(str(phone) for phone in contact.phones))


@bot_commands.register(
    "change-phone",
    args=["contact name", "old phone number", "new phone number"],
    description="Replace one of the contact's saved phone numbers with a new one.",
)
def change_phone(args: CommandArgs, context: CommandContext) -> None:
    name, old_phone, new_phone = args
    contacts_service = context["contacts_service"]

    try:
        contacts_service.update_contact(name, phone=(old_phone, new_phone))
        print("Contact updated.")
    except ContactNotFoundError:
        print("Contact doesn't exist.")


@bot_commands.register(
    "rm-phone",
    args=["contact name", "phone number"],
    description="Delete a specific phone number from a contact.",
)
def delete_phone(args: CommandArgs, context: CommandContext) -> None:
    name, phone = args
    contacts_service = context["contacts_service"]

    try:
        contacts_service.delete_phone(name, phone=phone)
        print("Phone number deleted.")
    except ContactNotFoundError:
        print("Contact doesn't exist.")


@bot_commands.register(
    "label-phone",
    args=["contact name", "phone number", "label"],
    description="Assign a label to one of the contact's phone numbers.",
)
def add_phone_label(args: CommandArgs, context: CommandContext) -> None:
    name, phone, label = args
    contacts_service = context["contacts_service"]

    try:
        contacts_service.add_phone_label(name, phone=phone, label=label)
        print("Phone label added.")
    except ContactNotFoundError:
        print("Contact doesn't exist.")


@bot_commands.register(
    "unlabel-phone",
    args=["contact name", "phone number"],
    description="Remove the label from one of the contact's phone numbers.",
)
def delete_phone_label(args: CommandArgs, context: CommandContext) -> None:
    name, phone = args
    contacts_service = context["contacts_service"]

    try:
        contacts_service.delete_phone_label(name, phone=phone)
        print("Phone label deleted.")
    except ContactNotFoundError:
        print("Contact doesn't exist.")


# ------------------------------------------------
# Commands for contact emails management
# ------------------------------------------------


@bot_commands.register(
    "add-email",
    args=["contact name", "email"],
    description="Add an email address to a contact.",
)
def add_email(args: CommandArgs, context: CommandContext) -> None:
    name, email = args
    contacts_service = context["contacts_service"]

    try:
        contacts_service.add_email(name, email=email)
        print("Email added.")
    except ContactNotFoundError:
        print("Contact doesn't exist.")


@bot_commands.register(
    "emails",
    args=["contact name"],
    description="List all email addresses saved for a contact.",
)
def list_emails(args: CommandArgs, context: CommandContext) -> None:
    name = args[0]
    contacts_service = context["contacts_service"]

    contact = contacts_service.get_contact(name)
    if not contact:
        print("Contact doesn't exist.")
        return

    if not contact.emails:
        print("Contact doesn't have an email set.")
        return

    print("\n".join(str(email) for email in contact.emails))


@bot_commands.register(
    "change-email",
    args=["contact name", "old email", "new email"],
    description="Replace one saved email address with another.",
)
def change_email(args: CommandArgs, context: CommandContext) -> None:
    name, old_email, new_email = args
    contacts_service = context["contacts_service"]

    try:
        contacts_service.change_email(
            name,
            old_email=old_email,
            new_email=new_email,
        )
        print("Email updated.")
    except ContactNotFoundError:
        print("Contact doesn't exist.")


@bot_commands.register(
    "rm-email",
    args=["contact name", "email"],
    description="Delete an email address from a contact.",
)
def delete_email(args: CommandArgs, context: CommandContext) -> None:
    name, email = args
    contacts_service = context["contacts_service"]

    try:
        contacts_service.delete_email(name, email=email)
        print("Email deleted.")
    except ContactNotFoundError:
        print("Contact doesn't exist.")


@bot_commands.register(
    "label-email",
    args=["contact name", "email", "label"],
    description="Assign a label to one of the contact's email addresses.",
)
def add_email_label(args: CommandArgs, context: CommandContext) -> None:
    name, email, label = args
    contacts_service = context["contacts_service"]

    try:
        contacts_service.add_email_label(name, email=email, label=label)
        print("Email label added.")
    except ContactNotFoundError:
        print("Contact doesn't exist.")


@bot_commands.register(
    "unlabel-email",
    args=["contact name", "email"],
    description="Remove the label from one of the contact's email addresses.",
)
def delete_email_label(args: CommandArgs, context: CommandContext) -> None:
    name, email = args
    contacts_service = context["contacts_service"]

    try:
        contacts_service.delete_email_label(name, email=email)
        print("Email label deleted.")
    except ContactNotFoundError:
        print("Contact doesn't exist.")


# ------------------------------------------------
# Commands for contact addresses management
# ------------------------------------------------


@bot_commands.register(
    "add-address",
    args=["contact name", "address"],
    description="Add a postal address to a contact.",
)
def add_address(args: CommandArgs, context: CommandContext) -> None:
    name, address = args
    contacts_service = context["contacts_service"]

    try:
        contacts_service.add_address(name, address=address)
        print("Address added.")
    except ContactNotFoundError:
        print("Contact doesn't exist.")


@bot_commands.register(
    "change-address",
    args=["contact name", "old address", "new address"],
    description="Replace one saved address with another.",
)
def change_address(args: CommandArgs, context: CommandContext) -> None:
    name, old_address, new_address = args
    contacts_service = context["contacts_service"]

    try:
        contacts_service.change_address(
            name,
            old_address=old_address,
            new_address=new_address,
        )
        print("Address updated.")
    except ContactNotFoundError:
        print("Contact doesn't exist.")


@bot_commands.register(
    "addresses",
    args=["contact name"],
    description="List all addresses saved for a contact.",
)
def list_addresses(args: CommandArgs, context: CommandContext) -> None:
    name = args[0]
    contacts_service = context["contacts_service"]

    contact = contacts_service.get_contact(name)
    if not contact:
        print("Contact doesn't exist.")
        return

    if not contact.addresses:
        print("Contact doesn't have an address set.")
        return

    print("\n".join(str(address) for address in contact.addresses))


@bot_commands.register(
    "rm-address",
    args=["contact name", "address"],
    description="Delete an address from a contact.",
)
def delete_address(args: CommandArgs, context: CommandContext) -> None:
    name, address = args
    contacts_service = context["contacts_service"]

    try:
        contacts_service.delete_address(name, address=address)
        print("Address deleted.")
    except ContactNotFoundError:
        print("Contact doesn't exist.")


@bot_commands.register(
    "label-address",
    args=["contact name", "address", "label"],
    description="Assign a label to one of the contact's addresses.",
)
def add_address_label(args: CommandArgs, context: CommandContext) -> None:
    name, address, label = args
    contacts_service = context["contacts_service"]

    try:
        contacts_service.add_address_label(name, address=address, label=label)
        print("Address label added.")
    except ContactNotFoundError:
        print("Contact doesn't exist.")


@bot_commands.register(
    "unlabel-address",
    args=["contact name", "address"],
    description="Remove the label from one of the contact's addresses.",
)
def delete_address_label(args: CommandArgs, context: CommandContext) -> None:
    name, address = args
    contacts_service = context["contacts_service"]

    try:
        contacts_service.delete_address_label(name, address=address)
        print("Address label deleted.")
    except ContactNotFoundError:
        print("Contact doesn't exist.")


# ------------------------------------------------
# Commands for contact birthday management
# ------------------------------------------------


@bot_commands.register(
    "set-birthday",
    args=["contact name", "birthday"],
    description="Set or update a contact's birthday.",
)
def set_birthday(args: CommandArgs, context: CommandContext) -> None:
    name, birthday = args
    contacts_service = context["contacts_service"]

    try:
        match contacts_service.add_birthday(name, birthday=birthday):
            case "added":
                print("Birthday added.")
            case "updated":
                print("Birthday updated.")
    except ContactNotFoundError:
        print("Contact doesn't exist.")


@bot_commands.register(
    "birthday",
    args=["contact name"],
    description="Display the saved birthday for a contact.",
)
def show_birthday(args: CommandArgs, context: CommandContext) -> None:
    name = args[0]
    contacts_service = context["contacts_service"]

    contact = contacts_service.get_contact(name)
    if contact:
        print(contact.birthday or "Contact doesn't have a birthday set.")
    else:
        print("Contact doesn't exist.")


@bot_commands.register(
    "rm-birthday",
    args=["contact name"],
    description="Remove the saved birthday from a contact.",
)
def delete_birthday(args: CommandArgs, context: CommandContext) -> None:
    name = args[0]
    contacts_service = context["contacts_service"]

    try:
        contacts_service.delete_birthday(name)
        print("Birthday deleted.")
    except ContactNotFoundError:
        print("Contact doesn't exist.")


@bot_commands.register(
    "upcoming",
    optional_args=["days"],
    description="Show upcoming birthdays and their congratulation dates.",
)
def list_upcoming_birthdays(context: CommandContext) -> None:
    contacts = context["contacts"]

    days = int(args[0]) if args else 7

    if not contacts:
        print("No contacts.")
        return

    if contacts.birthdays_count == 0:
        print("No contacts with birthdays.")
        return

    upcoming_birthdays = contacts.get_upcoming_birthdays(days)

    if not upcoming_birthdays:
        print("No contacts with upcoming birthdays.")
        return

    print(
        "\n".join(
            f"{upcoming_birthday['name']}: {upcoming_birthday['birthday']} (Congratulate: {upcoming_birthday['congratulation_date']})"
            for upcoming_birthday in upcoming_birthdays
        )
    )


# ================================================
# Commands for notes management
# ================================================


@bot_commands.register(
    "open",
    args=["note name"],
    description="Open the note editor to create or update a note.",
)
def edit_note(args: CommandArgs, context: CommandContext) -> None:
    name = args[0]
    notes_service = context["notes_service"]

    # Pre-fill if note already exists
    existing_note = notes_service.get_note(name)
    initial_text = existing_note.content.value if existing_note else ""

    print(f"Opening editor for note '{name}'...")
    final_content = open_editor(title=name, initial_text=initial_text)

    if final_content is not None:
        match notes_service.add_or_update_note(name, final_content):
            case "added":
                print(f"Note '{name}' created and saved.")
            case "updated":
                print(f"Note '{name}' updated.")
    else:
        print("Changes discarded.")


@bot_commands.register(
    "view",
    args=["note name"],
    description="Display the full content of a note.",
)
def show_note(args: CommandArgs, context: CommandContext) -> None:
    name = args[0]
    notes_service = context["notes_service"]

    note = notes_service.get_note(name)
    if not note:
        print("Note doesn't exist.")
        return

    console.print(note.content)


@bot_commands.register(
    "notes",
    description="Show all saved notes.",
)
def list_notes(context: CommandContext) -> None:
    notes = context["notes"]
    if not notes:
        print("No notes.")
        return
    print("\n".join(str(note) for note in notes.values()))


@bot_commands.register(
    "rename-note",
    args=["old note name", "new note name"],
    description="Rename an existing note.",
)
def rename_note(args: CommandArgs, context: CommandContext) -> None:
    old_name, new_name = args
    notes_service = context["notes_service"]

    try:
        match notes_service.rename_note(old_name, new_name):
            case "renamed":
                print(f"Note '{old_name}' renamed to '{new_name}'.")
            case "skipped":
                print(f"Note name is already '{new_name}'.")
    except NoteNotFoundError:
        print("Note doesn't exist.")
    except NoteAlreadyExistsError:
        print("Note with new name already exists.")


@bot_commands.register(
    "rm-note",
    args=["note name"],
    description="Delete a note.",
)
def delete_note(args: CommandArgs, context: CommandContext) -> None:
    name = args[0]
    notes_service = context["notes_service"]

    try:
        notes_service.delete_note(name)
        print(f"Note '{name}' deleted.")
    except NoteNotFoundError:
        print("Note doesn't exist.")


@bot_commands.register(
    "tag",
    args=["note name", "tag"],
    description="Attach a tag to a note.",
)
def add_note_tag(args: CommandArgs, context: CommandContext) -> None:
    name, tag = args
    notes_service = context["notes_service"]

    try:
        added_tags = notes_service.add_note_tags(name, [tag])
        if added_tags:
            print(f"Added '{tag}' tag to '{name}'.")
        else:
            print(f"Tag '{tag}' is already set on '{name}'.")
    except NoteNotFoundError:
        print("Note doesn't exist.")


@bot_commands.register(
    "tags",
    description="List all note tags with their usage counts.",
)
def list_note_tags(context: CommandContext) -> None:
    notes = context["notes"]
    notes_service = context["notes_service"]

    if not notes:
        print("No notes.")
        return

    tag_counts = notes_service.list_note_tags()
    if not tag_counts:
        print("No note tags.")
        return

    print("\n".join(f"{tag}: {count}" for tag, count in tag_counts))


@bot_commands.register(
    "untag",
    args=["note name", "tag"],
    description="Remove a tag from a note.",
)
def delete_note_tag(args: CommandArgs, context: CommandContext) -> None:
    name, tag = args
    notes_service = context["notes_service"]

    try:
        removed_tags = notes_service.remove_note_tags(name, [tag])
        if removed_tags:
            print(f"Deleted '{tag}' tag from '{name}'.")
        else:
            print(f"Tag '{tag}' is not set on '{name}'.")
    except NoteNotFoundError:
        print("Note doesn't exist.")


@bot_commands.register(
    "search-notes",
    args=["query"],
    description="Search note titles and contents using fuzzy matching.",
)
def search_notes(args: CommandArgs, context: CommandContext) -> None:
    query = args[0]
    notes = context["notes"]
    notes_service = context["notes_service"]

    if not notes:
        print("No notes available to search.")
        return

    matches = notes_service.search_notes(query, score_cutoff=60.0)

    if not matches:
        print(f"No match found for '{query}'.")
        return

    print("Suggested notes:")
    for note, score, name_res, content_res in matches:
        note_name = note.name.value
        title_text = Text("- ")
        if name_res and name_res.score == score:
            # Highlight title
            title_text.append(note_name[: name_res.dest_start])
            title_text.append(
                note_name[name_res.dest_start : name_res.dest_end], style="bold green"
            )
            title_text.append(note_name[name_res.dest_end :])
        else:
            title_text.append(note_name)

        if note.tags:
            tags_text = " ".join(f"[{tag.value}]" for tag in note.tags)
            title_text.append(f" {tags_text}", style="dim")

        console.print(title_text)

        if content_res and content_res.score == score:
            # Highlight content snippet
            note_content = note.content.value
            start = max(0, content_res.dest_start - 20)
            end = min(len(note_content), content_res.dest_end + 20)

            content_snippet = Text("  Content match: ")
            if start > 0:
                content_snippet.append("...")

            content_snippet.append(note_content[start : content_res.dest_start])
            content_snippet.append(
                note_content[content_res.dest_start : content_res.dest_end],
                style="bold green",
            )
            content_snippet.append(note_content[content_res.dest_end : end])

            if end < len(note_content):
                content_snippet.append("...")

            console.print(content_snippet)


@bot_commands.register(
    "search-by-tag",
    args=["tag"],
    description="Find all notes that have the given tag.",
)
def search_notes_by_tag(args: CommandArgs, context: CommandContext) -> None:
    tag = args[0]
    notes = context["notes"]
    notes_service = context["notes_service"]

    if not notes:
        print("No notes available to search.")
        return

    found_notes = notes_service.search_notes_by_tag(tag)
    if not found_notes:
        print(f"No notes found with tag '{tag}'.")
        return

    print("\n".join(str(note) for note in found_notes))


class StopCommandsLoop(Exception):
    pass


@bot_commands.register(
    "bye",
    "exit",
    "close",
    "quit",
    description="Exit the interactive assistant loop.",
)
def say_goodbye() -> None:
    print("Good bye!")
    raise StopCommandsLoop
