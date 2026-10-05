import subprocess
import sys
from os import login_tty, path
from pathlib import Path

from rich.text import Text
from textual import on, work
from textual.app import App, ComposeResult
from textual.binding import Keymap
from textual.color import Lab
from textual.containers import Container, Horizontal, Vertical
from textual.widget import Widget
from textual.widgets import (
    Checkbox,
    DirectoryTree,
    Footer,
    Input,
    Label,
    Log,
    RichLog,
    Select,
    Static,
    TabbedContent,
    TabPane,
)
from textual.worker import get_current_worker


def spawn_tab(content: str, name: str, tab_id):
    return TabPane(name, Static(content), id=tab_id)


class ScopeLogApp(App):

    tail_proc: subprocess.Popen | None = None
    grep_proc: subprocess.Popen | None = None
    CSS_PATH = "app.tcss"
    FILE_PATH: Path | None = None
    high_l = False
    reg_f = False
    sens_f = False
    foll_f = False
    BINDINGS = [
        ("s", "search", "Search"),
        ("g", "follow", "Follow"),
        ("TAB", "switch_source", "Source"),
        ("q", "quit", "Quit"),
    ]

    def stop_follow_processes(self) -> None:
        for proc in (self.grep_proc, self.tail_proc):
            if proc and proc.poll() is None:
                proc.terminate()
                try:
                    proc.wait(timeout=0.2)
                except subprocess.TimeoutExpired:
                    proc.kill()
        self.grep_proc = None
        self.tail_proc = None

    def on_unmount(self) -> None:
        self.stop_follow_processes()

    def top_container(self):
        logs = TabbedContent(id="logs")
        logs.border_title = "logs"
        logs.can_focus = True
        sources = DirectoryTree("./", id="sources")
        sources.border_title = "sources"
        sources.can_focus = True
        return logs, sources

    def compose(self) -> ComposeResult:
        with Vertical(id="app"):
            yield from self.compose_files()
            yield from self.compose_filters()
            yield self.compose_footer()

    def compose_files(self) -> ComposeResult:
        with Horizontal(id="files"):
            logs, sources = self.top_container()
            yield sources
            yield logs

    def compose_filters(self) -> ComposeResult:
        container = Container(id="filter-grid")
        container.border_title = "filters"

        with container:
            yield from self.compose_search()

    def compose_search(self) -> ComposeResult:
        with Vertical(id="search-container"):
            yield Label("Search:")
            yield Input(placeholder="Search logs...", id="search")
            with Horizontal(id="boxes"):
                yield Label("Highlight:")
                yield Checkbox(id="highlight-box")

                yield Label("Regex:")
                yield Checkbox(id="regex-box")

                yield Label("Follow:")
                yield Checkbox(id="follow-box")

                yield Label("Case-insensitive:")
                yield Checkbox(id="case-insensitive-box")

    def compose_footer(self) -> Static:
        return Static(
            "[s] Search  [g] Follow  [Tab] Source  [q] Quit",
            id="footer",
            markup=False,
        )

    def action_search(self):
        self.query_one("#search").focus()

    def action_follow(self):
        box = self.query_one("#follow-box", Checkbox)
        box.value = not box.value

    def action_switch_source(self):
        self.screen.focus_next()

    @on(Checkbox.Changed, "#case-insensitive-box")
    def set_insensitivity(self, event: Checkbox.Changed):
        self.sens_f = event.value

    @on(Checkbox.Changed, "#regex-box")
    def set_regex(self, event: Checkbox.Changed):
        self.reg_f = event.value

    @on(Checkbox.Changed, "#follow-box")
    def set_follow(self, event: Checkbox.Changed):
        self.foll_f = event.value
        if not self.foll_f:
            self.stop_follow_processes()

    @on(Checkbox.Changed, "#highlight-box")
    def set_highlight(self, event: Checkbox.Changed):
        self.high_l = event.value

    @on(Input.Submitted, "#search")
    @work(thread=True)
    def find_in_text(self, event: Input.Submitted):
        self.stop_follow_processes()
        logs_tabbed = self.query_one("#logs", TabbedContent)
        pattern = event.value
        if self.FILE_PATH is None:
            return

        if self.foll_f:
            self.follow_logs_worker(pattern)
            return

        cmd = ["grep"]
        if self.sens_f:
            cmd.append("-i")

        if self.high_l:
            cmd.append("--color=always")

        if self.reg_f:
            cmd.append("-E")

        cmd.extend([pattern, str(self.FILE_PATH)])

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
        )
        active_pane = logs_tabbed.get_pane(logs_tabbed.active)
        tab_stat = active_pane.query_one(RichLog)
        out = result.stdout if result.stdout else "No matches found."
        formatted = Text.from_ansi(out) if self.high_l else out
        tab_stat.clear()
        tab_stat.write(formatted)

    @on(DirectoryTree.FileSelected, "#sources")
    def open_selected_log(self, ev: DirectoryTree.FileSelected) -> None:
        self.stop_follow_processes()
        self.FILE_PATH = ev.path
        tab_id = f"tab-{hash(self.FILE_PATH)}"
        logs_tabbed: Widget = self.query_one("#logs", TabbedContent)

        try:
            logs_tabbed.active = tab_id
            return
        except Exception:
            pass

        log_widget = RichLog(id=f"log-{tab_id}")
        new_pane: TabPane = TabPane(self.FILE_PATH.name, log_widget, id=tab_id)
        logs_tabbed.add_pane(new_pane)
        logs_tabbed.active = tab_id

        self.load_file(self.FILE_PATH, log_widget)

    @work(thread=True)
    def load_file(self, path: Path, log_widget: RichLog) -> None:
        try:
            with open(path, encoding="utf-8", errors="replace") as file:
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

    @work(thread=True, exclusive=True)
    def follow_logs_worker(self, pattern: str):
        self.stop_follow_processes()
        logs_tabbed = self.query_one("#logs", TabbedContent)
        active_pane = logs_tabbed.get_pane(logs_tabbed.active)
        tab = active_pane.query_one(RichLog)
        self.call_from_thread(tab.clear)

        self.tail_proc = subprocess.Popen(
            ["tail", "-f", str(self.FILE_PATH)],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            bufsize=1,
        )

        grep_cmd = ["grep", "--line-buffered"]

        if self.sens_f:
            grep_cmd.append("-i")

        if self.reg_f:
            grep_cmd.append("-E")

        if self.high_l:
            grep_cmd.append("--color=always")

        grep_cmd.append(pattern)

        self.grep_proc = subprocess.Popen(
            grep_cmd,
            stdin=self.tail_proc.stdout,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
            bufsize=1,
        )

        if self.tail_proc.stdout:
            self.tail_proc.stdout.close()

        worker = get_current_worker()
        if self.grep_proc.stdout:
            for line in iter(self.grep_proc.stdout.readline, ""):
                if worker.is_cancelled:
                    break
                clean_line = line.rstrip("\n")
                formatted = Text.from_ansi(clean_line) if self.high_l else clean_line
                self.call_from_thread(tab.write, formatted)


if __name__ == "__main__":
    app = ScopeLogApp()
    app.run()
