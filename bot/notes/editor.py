from prompt_toolkit.application import Application
from prompt_toolkit.formatted_text import HTML
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout.containers import HSplit, Window
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.widgets import TextArea


def open_editor(title: str, initial_text: str = "") -> str | None:
    title_bar = Window(
        height=1,
        content=FormattedTextControl(f" Editing note: {title} ", style="class:title"),
        style="bg:white fg:black bold",
    )
    text_area = TextArea(text=initial_text, multiline=True, scrollbar=True)
    status_bar = Window(
        height=1,
        content=FormattedTextControl(
            HTML(
                ' <style bg="white" fg="black"> [Ctrl-S] Save Note </style>  <style bg="white" fg="black"> [Ctrl-Q] Discard </style>'
            )
        ),
        style="class:status",
    )
    root_container = HSplit([title_bar, text_area, status_bar])
    layout = Layout(root_container)

    bindings = KeyBindings()

    @bindings.add("c-s")
    def save(event):
        event.app.exit(result=text_area.text)

    @bindings.add("c-q")
    def quit(event):
        event.app.exit(result=None)

    app = Application(
        layout=layout,
        key_bindings=bindings,
        full_screen=True,
        mouse_support=True,
    )
    return app.run()
