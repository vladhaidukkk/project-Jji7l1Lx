from rich.console import Console
from rich.text import Text

from bot.commands import CommandArgs, CommandContext, CommandsRegistry
from bot.contacts import ContactAlreadyExistsError, ContactNotFoundError
from bot.notes import Note, NoteAlreadyExistsError, NoteNotFoundError
from bot.notes.editor import open_editor

console = Console()
bot_commands = CommandsRegistry()


@bot_commands.register("hello")
def say_hello() -> None:
    print("How can I help you?")


@bot_commands.register("add", args=["name"], optional_args=["phone number"])
def add_contact(args: CommandArgs, context: CommandContext) -> None:
    name, phone = args
    contacts_service = context["contacts_service"]

    try:
        match contacts_service.add_contact(name, phone=phone):
            case "added":
                print("Contact added.")
            case "updated:phone":
                print("Phone number added.")
    except ContactAlreadyExistsError:
        print("Contact already exists.")


@bot_commands.register("change", args=["name", "old phone number", "new phone number"])
def change_phone(args: CommandArgs, context: CommandContext) -> None:
    name, old_phone, new_phone = args
    contacts_service = context["contacts_service"]

    try:
        contacts_service.update_contact(name, phone=(old_phone, new_phone))
        print("Contact updated.")
    except ContactNotFoundError:
        print("Contact doesn't exist.")


@bot_commands.register("phone", args=["name"])
def show_phone(args: CommandArgs, context: CommandContext) -> None:
    name = args[0]
    contacts_service = context["contacts_service"]

    contact = contacts_service.get_contact(name)
    if not contact:
        print("Contact doesn't exist.")
        return

    if not contact.phones:
        print("This contact doesn't have a phone number.")
        return

    print(contact.phones[0])


@bot_commands.register("all")
def show_all(context: CommandContext) -> None:
    contacts = context["contacts"]
    if contacts:
        print(
            "\n".join(
                f"{contact.name}: {contact.phones[0] if contact.phones else '-'}"
                for contact in contacts.values()
            )
        )
    else:
        print("No contacts.")


@bot_commands.register("add-birthday", args=["name", "birthday"])
def add_birthday(args: CommandArgs, context: CommandContext) -> None:
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


@bot_commands.register("show-birthday", args=["name"])
def show_birthday(args: CommandArgs, context: CommandContext) -> None:
    name = args[0]
    contacts_service = context["contacts_service"]

    contact = contacts_service.get_contact(name)
    if contact:
        print(contact.birthday or "Contact doesn't have a birthday set.")
    else:
        print("Contact doesn't exist.")


@bot_commands.register("add-address", args=["name", "address"])
def add_address(args: CommandArgs, context: CommandContext) -> None:
    name, address = args
    contacts_service = context["contacts_service"]

    try:
        match contacts_service.add_address(name, address=address):
            case "added":
                print("Address added.")
            case "updated":
                print("Address updated.")
    except ContactNotFoundError:
        print("Contact doesn't exist.")


@bot_commands.register("show-address", args=["name"])
def show_address(args: CommandArgs, context: CommandContext) -> None:
    name = args[0]
    contacts_service = context["contacts_service"]

    contact = contacts_service.get_contact(name)
    if contact:
        print(contact.address or "Contact doesn't have an address set.")
    else:
        print("Contact doesn't exist.")


@bot_commands.register("birthdays")
def birthdays(context: CommandContext) -> None:
    contacts = context["contacts"]

    if not contacts:
        print("No contacts.")
        return

    if contacts.birthdays_count == 0:
        print("No contacts with birthdays.")
        return

    upcoming_birthdays = contacts.get_upcoming_birthdays()
    if not upcoming_birthdays:
        print("No contacts with upcoming birthdays.")
        return

    print(
        "\n".join(
            f"{upcoming_birthday['name']}: {upcoming_birthday['birthday']} (Congratulate: {upcoming_birthday['congratulation_date']})"
            for upcoming_birthday in upcoming_birthdays
        )
    )


@bot_commands.register("delete", args=["name"])
def delete_contact(args: CommandArgs, context: CommandContext) -> None:
    name = args[0]
    contacts_service = context["contacts_service"]

    try:
        contacts_service.delete_contact(name)
        print(f"Contact '{name}' deleted.")
    except ContactNotFoundError:
        print("Contact doesn't exist.")


@bot_commands.register("note", args=["name"])
def edit_note(args: CommandArgs, context: CommandContext) -> None:
    name = args[0]
    notes_service = context["notes_service"]

    # Pre-fill if note already exists
    existing_note = notes_service.get_note(name)
    initial_text = existing_note.content if existing_note else ""

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


@bot_commands.register("notes")
def show_notes(context: CommandContext) -> None:
    notes = context["notes"]
    if not notes:
        print("No notes.")
        return

    def format_note(note: Note) -> str:
        content_preview = note.preview(30)
        return f"{note.name}: {content_preview}" if content_preview else note.name

    print("\n".join(format_note(note) for note in notes.values()))


@bot_commands.register("delete-note", args=["name"])
def delete_note(args: CommandArgs, context: CommandContext) -> None:
    name = args[0]
    notes_service = context["notes_service"]

    try:
        notes_service.delete_note(name)
        print(f"Note '{name}' deleted.")
    except NoteNotFoundError:
        print("Note doesn't exist.")


@bot_commands.register("rename-note", args=["old name", "new name"])
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


@bot_commands.register("search-notes", args=["query"])
def search_notes(args: CommandArgs, context: CommandContext) -> None:
    query = args[0]
    notes = context["notes"]
    notes_service = context["notes_service"]

    if not notes:
        print("No notes available to search.")
        return

    matches = notes_service.search_notes(query)

    if not matches:
        print(f"No match found for '{query}'.")
        return

    print("Suggested notes:")
    for note, score, name_res, content_res in matches:
        title_text = Text("- ")
        if name_res and name_res.score == score:
            # Highlight title
            title_text.append(note.name[: name_res.dest_start])
            title_text.append(
                note.name[name_res.dest_start : name_res.dest_end], style="bold green"
            )
            title_text.append(note.name[name_res.dest_end :])
        else:
            title_text.append(note.name)

        console.print(title_text)

        if content_res and content_res.score == score:
            # Highlight content snippet
            start = max(0, content_res.dest_start - 20)
            end = min(len(note.content), content_res.dest_end + 20)

            content_snippet = Text("  Content match: ")
            if start > 0:
                content_snippet.append("...")

            content_snippet.append(note.content[start : content_res.dest_start])
            content_snippet.append(
                note.content[content_res.dest_start : content_res.dest_end],
                style="bold green",
            )
            content_snippet.append(note.content[content_res.dest_end : end])

            if end < len(note.content):
                content_snippet.append("...")

            console.print(content_snippet)


class StopCommandsLoop(Exception):
    pass


@bot_commands.register("exit", "close", "quit", "bye")
def say_goodbye() -> None:
    print("Good bye!")
    raise StopCommandsLoop
