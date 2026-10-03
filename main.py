import sys
from os import path
from pathlib import Path

from textual import on
from textual.app import App, ComposeResult
from textual.binding import Keymap
from textual.containers import Horizontal, Vertical
from textual.widgets import DirectoryTree, Footer, Static

from sources import Sources


class LazyLogApp(App):
    """A TUI around `tail`, `grep`, `less`, `journalctl`, etc. for investigating logs."""

    CSS = """
#app {
}
#sources:focus, #logs:focus, #filters:focus {
    border: round white;
}

#sources {
    padding: 1;
    width: 30%;
    border: round $accent;
    background: black;
    }

#logs {
    padding: 1;
    height: 1fr;
    border: round $accent;
}

#filters {
    height: 4;
    border: round $accent;
}

#footer {
    height: 1;
}
"""
    BINDINGS = [
        ("/", "search", "Search"),
        ("f", "filter", "Filter"),
        ("g", "follow", "Follow"),
        ("TAB", "switch_source", "Source"),
        ("q", "quit", "Quit"),
    ]

    def compose(self) -> ComposeResult:
        with Vertical(id="app"):
            with Horizontal(id="files"):
                logs = Static(id="logs")
                logs.border_title = "logs"
                logs.can_focus = True
                sources = DirectoryTree("./", id="sources")
                sources.border_title = "sources"
                sources.can_focus = True
                yield sources
                yield logs
            filters = Static(id="filters")
            filters.border_title = "filters"
            filters.can_focus = True
            yield filters
            yield Static(
                "[/] Search  [f] Filter  [g] Follow  [Tab] Source  [q] Quit",
                id="footer",
                markup=False,
            )

    def action_search(self):
        pass

    def action_filter(self):
        pass

    def action_follow(self):
        pass

    def action_switch_source(self):
        self.screen.focus_next()

    def action_quit(self):
        sys.exit()

    @on(DirectoryTree.FileSelected, "#sources")
    def open_selected_log(self, ev: DirectoryTree.FileSelected) -> None:
        file_path: Path = ev.path
        content: str | None = None
        try:
            content = file_path.read_text(encoding="utf-8", errors="replace")
        except Exception as e:
            content = f"Error reading file: {e}"

        logs = self.query_one("#logs", Static)
        logs.update(content)


if __name__ == "__main__":
    app = LazyLogApp()
    app.run()
