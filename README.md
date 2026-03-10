# Assistant Bot Project

A CLI-based assistant bot for managing contacts and notes.

## Getting Started

Follow these steps to set up the project locally:

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd project-Jji7l1Lx
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv .venv
   ```

3. **Activate the virtual environment:**
   - **MacOS/Linux:**
     ```bash
     source .venv/bin/activate
     ```
   - **Windows:**
     ```bash
     .venv\Scripts\activate
     ```

4. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

5. **Run the bot:**
   ```bash
   python -m bot
   ```

## Working with Git

To maintain a clean and efficient workflow, follow these steps when starting a new task:

1. **Prepare your workspace:**
   Before starting, ensure your local `main` branch is up to date.
   ```bash
   git checkout main
   git pull origin main
   ```

2. **Create a feature branch:**
   Create a new branch for your task using a descriptive name (e.g., `feature/add-search-command`).
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make commits:**
   Work on your task and commit changes with clear, concise messages.
   ```bash
   git add .
   git commit -m "description of your changes"
   ```

4. **Push and create a PR:**
   Push your branch to the remote repository.
   ```bash
   git push origin feature/your-feature-name
   ```
   Open a Pull Request (PR) on the repository hosting platform.

5. **Request a Code Review:**
   - Add the **Team Lead** as a reviewer in the PR settings.
   - Send a message to the Team Lead (via Slack) notifying them that the PR is ready for review.

## Project Overview

### Project Hierarchy

```
/
└── bot/
    ├── __main__.py          # Application entry point & main loop
    ├── bot_commands.py      # Definition and registration of all bot commands
    ├── commands/            # Core command processing logic
    │   ├── dispatcher.py    # Handles user input and command execution
    │   ├── registry.py      # Manages command registration
    │   └── errors.py        # Command-related custom exceptions
    ├── contacts/            # Business logic for contact management
    │   ├── models.py        # Data models (ContactsBook, Record, etc.)
    │   ├── service.py       # Services for contact operations
    │   └── errors.py        # Contact-related custom exceptions
    └── notes/               # Business logic for notes management
        ├── models.py        # Data models (NotesBook, Note, etc.)
        ├── service.py       # Services for note operations
        ├── editor.py        # Interactive note editor (CLI-based)
        └── errors.py        # Note-related custom exceptions
```

### Core Components

- **`bot/__main__.py`**: The application entry point. It initializes `ContactsService` and `NotesService`, manages the main loop, and ensures data is persisted to disk on exit.
- **`CommandsRegistry`**: A central class (`bot/commands/registry.py`) that stores all available commands and their metadata (arguments, aliases).
- **`CommandsDispatcher`**: Responsible for parsing user input, looking up commands in the registry, and invoking them with the correct context and arguments.
- **`ContactsService` & `NotesService`**: These services act as the primary interface for command functions to interact with the underlying data models (`ContactsBook`, `NotesBook`), enforcing business rules and handling data persistence.
- **Interactive Editor**: A utility in `bot/notes/editor.py` that allows seamless editing of note content using the system's default text editor from within the CLI.

### How to Add New Commands

All bot commands are defined in `bot/bot_commands.py`. To add a new command:

1. Use the `@bot_commands.register` decorator.
2. Define the function, specifying if it needs `args` (user-provided arguments) or `context` (injected services like `contacts_service` or `notes_service`).

Example:
```python
@bot_commands.register("search", args=["query"])
def search_contact(args: CommandArgs, context: CommandContext) -> None:
    query = args[0]
    # Implement search logic using context["contacts_service"]
    print(f"Searching for: {query}")
```

The `dispatcher` will automatically handle argument validation based on the `args` and `optional_args` provided in the decorator.
