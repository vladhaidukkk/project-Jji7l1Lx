import sys
from pathlib import Path

from bot.bot_commands import StopCommandsLoop, bot_commands
from bot.commands import (
    CommandNotFoundError,
    CommandsDispatcher,
    InvalidCommandArgumentsError,
)
from bot.contacts import ContactsBook, ContactsService
from bot.notes import NotesBook, NotesService

commands_dispatcher = CommandsDispatcher(bot_commands)


def parse_args(args: list[str]) -> tuple[Path, Path]:
    if len(args) > 2:
        print(f"Usage: python -m bot [path_to_contacts_book] [path_to_notes_book]")
        print(f"Expected 0, 1, or 2 arguments, got {len(args)}")
        sys.exit(1)

    contacts_path = Path(args[0]) if len(args) > 0 else Path("contacts.pkl")
    notes_path = Path(args[1]) if len(args) > 1 else Path("notes.pkl")
    return contacts_path, notes_path


def load_contacts(path: Path) -> ContactsBook:
    try:
        return ContactsBook.from_file(path)
    except IsADirectoryError:
        print(f"File is expected, not a directory: '{path.name}'")
        sys.exit(1)


def load_notes(path: Path) -> NotesBook:
    try:
        return NotesBook.from_file(path)
    except IsADirectoryError:
        print(f"File is expected, not a directory: '{path.name}'")
        sys.exit(1)


def handle_invalid_command_args_error(error: InvalidCommandArgumentsError) -> None:
    if error.required_args and error.optional_args:
        print(
            f"Give me {error.required_args_str} please, and optionally {error.optional_args_str}."
        )
    elif error.required_args:
        print(f"Give me {error.required_args_str} please.")
    elif error.optional_args:
        print(f"You can optionally provide {error.optional_args_str}.")
    else:
        print("This command doesn't take any arguments.")


def main() -> None:
    contacts_path, notes_path = parse_args(sys.argv[1:])

    contacts = load_contacts(contacts_path)
    contacts_service = ContactsService(contacts)

    notes = load_notes(notes_path)
    notes_service = NotesService(notes)

    # Run commands in a loop
    print("Welcome to the assistant bot!")
    try:
        while True:
            command, command_args = commands_dispatcher.input_command(
                "Enter a command: "
            )
            if not command:
                continue

            try:
                commands_dispatcher.run_command(
                    command,
                    *command_args,
                    contacts=contacts,
                    contacts_service=contacts_service,
                    notes=notes,
                    notes_service=notes_service,
                )
            except CommandNotFoundError:
                print("Invalid command.")
            except InvalidCommandArgumentsError as e:
                handle_invalid_command_args_error(e)
            except ValueError as e:
                print(e)
            except StopCommandsLoop:
                break
            except Exception as e:
                print(f"Whoops, an unexpected error occurred: {e}")
    finally:
        # Save contacts and notes at the end
        contacts.save(contacts_path)
        notes.save(notes_path)


if __name__ == "__main__":
    main()
