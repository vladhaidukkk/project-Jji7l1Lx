class NotesError(Exception):
    pass


class NoteAlreadyExistsError(NotesError):
    pass


class NoteNotFoundError(NotesError):
    pass
