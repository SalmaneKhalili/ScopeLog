import subprocess
import sys
from os import login_tty, path
from pathlib import Path

from textual import on, work
from textual.app import App, ComposeResult
from textual.binding import Keymap
from textual.containers import Container, Horizontal, Vertical
from textual.widget import Widget
from textual.widgets import (
    Checkbox,
    DirectoryTree,
    Footer,
    Input,
    Label,
    Log,
    Select,
    Static,
    TabbedContent,
    TabPane,
)
from textual.worker import Worker

from sources import Sources


def spawn_tab(content: str, name: str, tab_id):
    return TabPane(name, Static(content), id=tab_id)


class LazyLogApp(App):
    """A TUI around `tail`, `grep`, `less`, `journalctl`, etc. for investigating logs."""

    CSS_PATH = "app.tcss"
    FILE_PATH: Path | None = None

    BINDINGS = [
        ("slash", "search", "Search"),
        ("f", "filter", "Filter"),
        ("g", "follow", "Follow"),
        ("TAB", "switch_source", "Source"),
        ("q", "quit", "Quit"),
    ]

    def top_container(self):
        logs = TabbedContent(id="logs")
        logs.border_title = "logs"
        logs.can_focus = True
        sources = DirectoryTree("./", id="sources")
        sources.border_title = "sources"
        sources.can_focus = True
        return logs, sources

    def bott_container(self):
        input = Input(placeholder="Hello", value="test", id="search")
        selector = Select(
            options=[
                ("All Levels", "all"),
                ("ERROR", "error"),
                ("WARN", "warn"),
            ],
            value="all",
            id="level-select",
        )
        return input, selector

    def compose(self) -> ComposeResult:
        with Vertical(id="app"):
            with Horizontal(id="files"):
                logs, sources = self.top_container()
                yield sources
                yield logs
            container = Container(id="filter-grid")
            container.border_title = "filters"
            with container:
                input, selector = self.bott_container()
                search = Horizontal(
                    Label("Search: ", id="search_label"), input, id="search_container"
                )
                yield search
                # yield selector
            yield Static(
                "[/] Search  [f] Filter  [g] Follow  [Tab] Source  [q] Quit",
                id="footer",
                markup=False,
            )

    def action_search(self):
        self.query_one("#search").focus()

    def action_filter(self):
        pass

    def action_follow(self):
        pass

    def action_switch_source(self):
        self.screen.focus_next()

    @on(Input.Submitted, "#search")
    @work(thread=True)
    def find_in_text(self, event: Input.Submitted):
        logs_tabbed = self.query_one("#logs", TabbedContent)
        pattern = event.value
        if self.FILE_PATH == None:
            return
        result = subprocess.run(
            ["grep", "-E", "-i", pattern, self.FILE_PATH],
            capture_output=True,
            text=True,
        )
        active_pane = logs_tabbed.get_pane(logs_tabbed.active)
        tab_stat = active_pane.query_one(Log)
        out = result.stdout if result.stdout else "No matches found."
        tab_stat.clear()
        tab_stat.write(out)

    @on(DirectoryTree.FileSelected, "#sources")
    def open_selected_log(self, ev: DirectoryTree.FileSelected) -> None:
        self.FILE_PATH = ev.path
        content: str | None = None
        tab_id = f"tab-{hash(self.FILE_PATH)}"
        logs_tabbed: Widget = self.query_one("#logs", TabbedContent)

        try:
            logs_tabbed.active = tab_id
            return
        except Exception:
            pass
        try:
            content = self.FILE_PATH.read_text(encoding="utf-8", errors="replace")
        except Exception as e:
            content = f"Error reading file: {e}"

        log_widget = Log(id=f"log-{tab_id}")

        new_pane: TabPane = TabPane(self.FILE_PATH.name, log_widget, id=tab_id)
        logs_tabbed.add_pane(new_pane)
        logs_tabbed.active = tab_id

        self.load_file(self.FILE_PATH, log_widget)

    @work(thread=True)
    def load_file(self, path, log_widget: Log) -> None:
        try:
            with open(path, encoding="utf-8") as file:
                chunk = []
                for line in file:
                    chunk.append(line)
                    if len(chunk) >= 1000:
                        lines_to_write = "".join(chunk)
                        self.call_from_thread(log_widget.write, lines_to_write)
                        chunk.clear()
                if chunk:
                    self.call_from_thread(log_widget.write, "".join(chunk))

        except Exception as e:
            self.call_from_thread(log_widget.write, f"Error reading file: {e}")


if __name__ == "__main__":
    app = LazyLogApp()
    app.run()
