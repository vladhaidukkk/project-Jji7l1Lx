from pathlib import Path

import typer

from bot.bot_commands import StopCommandsLoop, bot_commands
from bot.commands import (
    CommandNotFoundError,
    CommandsDispatcher,
    InvalidCommandArgumentsError,
)
from bot.config import (
    APP_DESCRIPTION,
    APP_NAME,
    DEFAULT_CONTACTS_FILE,
    DEFAULT_HISTORY_FILE,
    DEFAULT_NOTES_FILE,
)
from bot.contacts import ContactsBook, ContactsService
from bot.notes import NotesBook, NotesService


def load_contacts(path: Path) -> ContactsBook:
    try:
        return ContactsBook.from_file(path)
    except IsADirectoryError:
        print(f"File is expected, not a directory: '{path.name}'")
        raise typer.Exit(code=1)


def load_notes(path: Path) -> NotesBook:
    try:
        return NotesBook.from_file(path)
    except IsADirectoryError:
        print(f"File is expected, not a directory: '{path.name}'")
        raise typer.Exit(code=1)


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


def run_bot(
    *,
    contacts_path: Path = DEFAULT_CONTACTS_FILE,
    notes_path: Path = DEFAULT_NOTES_FILE,
    history_path: Path = DEFAULT_HISTORY_FILE,
) -> None:
    commands_dispatcher = CommandsDispatcher(bot_commands, history_path)

    contacts = load_contacts(contacts_path)
    contacts_service = ContactsService(contacts)

    notes = load_notes(notes_path)
    notes_service = NotesService(notes)

    # Run commands in a loop
    print("Welcome to the assistant bot!")
    try:
        while True:
            try:
                command, command_args = commands_dispatcher.input_command(
                    "Enter a command: "
                )
                if not command:
                    continue

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


app = typer.Typer(
    name=APP_NAME,
    help=APP_DESCRIPTION,
    invoke_without_command=True,
    add_completion=False,
)


@app.callback()
def cli(
    contacts_path: Path = typer.Option(
        DEFAULT_CONTACTS_FILE,
        "--contacts-path",
        help="Path to the contacts pickle file.",
    ),
    notes_path: Path = typer.Option(
        DEFAULT_NOTES_FILE,
        "--notes-path",
        help="Path to the notes pickle file.",
    ),
) -> None:
    run_bot(
        contacts_path=contacts_path,
        notes_path=notes_path,
        history_path=DEFAULT_HISTORY_FILE,
    )


def main() -> None:
    app()


if __name__ == "__main__":
    main()
