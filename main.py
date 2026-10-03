import sys

from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical
from textual.widgets import DirectoryTree, Footer, Static


class LazyLogApp(App):
    """A TUI around `tail`, `grep`, `less`, `journalctl`, etc. for investigating logs."""

    CSS = """
#app {
}

#sources {
    width: 30%;
    border: round $accent;
    background: black;
    }

#logs {
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
                sources = DirectoryTree("./", id="sources")
                sources.border_title = "sources"
                yield sources
                yield logs
            filters = Static(id="filters")
            filters.border_title = "filters"
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
        pass

    def action_quit(self):
        sys.exit()


if __name__ == "__main__":
    app = LazyLogApp()
    app.run()
