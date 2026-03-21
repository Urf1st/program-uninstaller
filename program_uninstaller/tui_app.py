#!/usr/bin/env python3
"""
LinuxSweep — Package Remover & Leftover Cleaner
A Revo Uninstaller-like tool for Linux systems.

Place this file in the same folder as:
  pacget.py, progremover.py, leftoversearcher.py

Requires: pip install textual
"""

from pacget import get_all_packages
from progremover import remove_package
from leftoversearcher import leftover_searcher, remove_leftover

# ─── TUI ─────────────────────────────────────────────────────────────────────

from textual.app import App, ComposeResult
from textual.widgets import (
    Header, Footer, DataTable, Button, Label, Checkbox, Input
)
from textual.containers import Horizontal, Vertical, ScrollableContainer
from textual.screen import ModalScreen
from textual.binding import Binding
from textual import work, on
from rich.text import Text


CSS = """
Screen { background: #0d1117; }

Header { background: #161b22; color: #58a6ff; text-style: bold; }
Footer { background: #161b22; color: #8b949e; }

#sidebar {
    width: 22; background: #161b22;
    border-right: solid #30363d; padding: 1 1;
}
#sidebar Label { color: #8b949e; margin-bottom: 1; }
#sidebar Button { width: 100%; margin-bottom: 1; }

#btn-refresh { background: #21262d; color: #58a6ff; border: solid #30363d; }
#btn-refresh:hover { background: #30363d; }
#btn-remove { background: #b91c1c; color: #fecaca; border: solid #991b1b; }
#btn-remove:hover { background: #991b1b; }
#btn-exit { background: #21262d; color: #8b949e; border: solid #30363d; }
#btn-exit:hover { background: #30363d; color: #f0f6fc; }

#pkg-count { color: #3fb950; text-style: bold; margin-top: 1; }
#filter-input { margin-top: 1; margin-bottom: 1; border: solid #30363d; background: #0d1117; color: #f0f6fc; }

#main-area { background: #0d1117; padding: 0 1; }
#table-label { color: #58a6ff; text-style: bold; padding: 1 0 0 1; }

DataTable { background: #0d1117; height: 1fr; border: solid #21262d; }
DataTable > .datatable--header { background: #161b22; color: #58a6ff; text-style: bold; }
DataTable > .datatable--cursor { background: #1f6feb; color: #f0f6fc; }
DataTable > .datatable--even-row { background: #0d1117; }
DataTable > .datatable--odd-row { background: #161b22; }

#status-bar { height: 1; background: #161b22; color: #3fb950; padding: 0 2; }

ConfirmScreen { align: center middle; }
#dialog-box { background: #161b22; border: solid #30363d; padding: 2 3; width: 60; height: auto; max-height: 40; }
#dialog-title { text-style: bold; color: #f0f6fc; margin-bottom: 1; }
#dialog-body { color: #8b949e; margin-bottom: 2; }
.dialog-buttons { height: auto; align: center middle; }
.dialog-buttons Button { margin: 0 1; }
#btn-yes { background: #b91c1c; color: #fecaca; border: solid #991b1b; }
#btn-yes:hover { background: #991b1b; }
#btn-no { background: #21262d; color: #8b949e; border: solid #30363d; }
#btn-no:hover { background: #30363d; color: #f0f6fc; }

LeftoverScreen { align: center middle; }
#leftover-box { background: #161b22; border: solid #30363d; padding: 2 3; width: 80; height: 35; }
#leftover-title { text-style: bold; color: #f0f6fc; margin-bottom: 1; }
#leftover-scroll { height: 1fr; border: solid #21262d; background: #0d1117; margin-bottom: 1; }
#leftover-buttons { height: auto; align: center middle; }
#leftover-buttons Button { margin: 0 1; }
#btn-select-all { background: #1f6feb; color: #f0f6fc; border: solid #388bfd; }
#btn-select-all:hover { background: #388bfd; }
#btn-delete-leftovers { background: #b91c1c; color: #fecaca; border: solid #991b1b; }
#btn-delete-leftovers:hover { background: #991b1b; }
#btn-close-leftovers { background: #21262d; color: #8b949e; border: solid #30363d; }
#btn-close-leftovers:hover { background: #30363d; color: #f0f6fc; }

NotifyScreen { align: center middle; }
#notify-box { background: #161b22; border: solid #30363d; padding: 2 4; width: 50; height: auto; }
#notify-icon { text-style: bold; margin-bottom: 1; text-align: center; }
#notify-msg { color: #c9d1d9; margin-bottom: 2; text-align: center; }
#btn-ok { background: #1f6feb; color: #f0f6fc; border: solid #388bfd; width: 100%; }
#btn-ok:hover { background: #388bfd; }
"""


# ── Modal: confirm dialog ─────────────────────────────────────────────────────

class ConfirmScreen(ModalScreen):
    def __init__(self, title: str, body: str, **kwargs):
        super().__init__(**kwargs)
        self._title = title
        self._body = body

    def compose(self) -> ComposeResult:
        with Vertical(id="dialog-box"):
            yield Label(self._title, id="dialog-title")
            yield Label(self._body, id="dialog-body")
            with Horizontal(classes="dialog-buttons"):
                yield Button("Yes, delete", id="btn-yes", variant="error")
                yield Button("Cancel", id="btn-no")

    @on(Button.Pressed, "#btn-yes")
    def confirmed(self): self.dismiss(True)

    @on(Button.Pressed, "#btn-no")
    def cancelled(self): self.dismiss(False)


# ── Modal: notification ───────────────────────────────────────────────────────

class NotifyScreen(ModalScreen):
    def __init__(self, message: str, success: bool = True, **kwargs):
        super().__init__(**kwargs)
        self._message = message
        self._success = success

    def compose(self) -> ComposeResult:
        icon = "✓  Done" if self._success else "✗  Error"
        color = "#3fb950" if self._success else "#f85149"
        with Vertical(id="notify-box"):
            yield Label(Text(icon, style=f"bold {color}"), id="notify-icon")
            yield Label(self._message, id="notify-msg")
            yield Button("OK", id="btn-ok")

    @on(Button.Pressed, "#btn-ok")
    def close(self): self.dismiss()


# ── Modal: leftovers viewer ───────────────────────────────────────────────────

class LeftoverScreen(ModalScreen):
    def __init__(self, package_name: str, leftovers: list[str], **kwargs):
        super().__init__(**kwargs)
        self._package_name = package_name
        self._leftovers = leftovers

    def compose(self) -> ComposeResult:
        with Vertical(id="leftover-box"):
            yield Label(
                f"Leftovers found for: [bold #58a6ff]{self._package_name}[/]",
                id="leftover-title", markup=True
            )
            with ScrollableContainer(id="leftover-scroll"):
                for path in self._leftovers:
                    cb = Checkbox(path, value=False)
                    cb.add_class("leftover-cb")
                    yield cb
            with Horizontal(id="leftover-buttons"):
                yield Button("Select All", id="btn-select-all")
                yield Button("Delete Selected", id="btn-delete-leftovers", variant="error")
                yield Button("Close", id="btn-close-leftovers")

    @on(Button.Pressed, "#btn-select-all")
    def select_all(self):
        for cb in self.query(".leftover-cb"):
            cb.value = True

    @on(Button.Pressed, "#btn-delete-leftovers")
    def delete_leftovers(self):
        selected = [str(cb.label) for cb in self.query(".leftover-cb") if cb.value]
        if not selected:
            self.app.push_screen(NotifyScreen("No items selected.", success=False))
            return

        paths_str = "\n".join(f"  - {p}" for p in selected[:5])
        if len(selected) > 5:
            paths_str += f"\n  ... and {len(selected) - 5} more"

        def on_confirmed(confirmed):
            if not confirmed:
                return
            failed = [p for p in selected if not remove_leftover(p)]
            self.dismiss()
            if failed:
                self.app.push_screen(NotifyScreen(f"Deleted with {len(failed)} error(s).", success=False))
            else:
                self.app.push_screen(NotifyScreen(f"Successfully removed {len(selected)} leftover item(s)."))

        self.app.push_screen(
            ConfirmScreen(
                "Delete leftover files?",
                f"Permanently delete {len(selected)} item(s):\n{paths_str}\n\nThis cannot be undone."
            ),
            callback=on_confirmed
        )

    @on(Button.Pressed, "#btn-close-leftovers")
    def close(self): self.dismiss()


# ── Main App ──────────────────────────────────────────────────────────────────

class LinuxSweep(App):
    CSS = CSS
    TITLE = "LinuxSweep"
    BINDINGS = [
        Binding("ctrl+r", "refresh", "Refresh"),
        Binding("ctrl+d", "remove_selected", "Delete"),
        Binding("ctrl+a", "select_all", "Select All"),
        Binding("escape", "quit", "Quit"),
    ]

    def __init__(self):
        super().__init__()
        self._packages: list[dict] = []
        self._filtered: list[dict] = []
        self._checked: set[int] = set()

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        with Horizontal():
            with Vertical(id="sidebar"):
                yield Label("LinuxSweep")
                yield Input(placeholder="Filter packages...", id="filter-input")
                yield Button("Refresh List", id="btn-refresh")
                yield Button("Remove Selected", id="btn-remove")
                yield Button("Exit", id="btn-exit")
                yield Label("", id="pkg-count")
            with Vertical(id="main-area"):
                yield Label("Installed Packages", id="table-label")
                yield DataTable(id="pkg-table", cursor_type="row")
        yield Label("Ready - select packages and press Remove Selected", id="status-bar")
        yield Footer()

    def on_mount(self):
        table = self.query_one("#pkg-table", DataTable)
        table.add_column("", width=3)
        table.add_column("Package Name", width=40)
        table.add_column("Source", width=12)
        self.action_refresh()

    # ── Data loading ──────────────────────────────────────────────────────────

    @work(thread=True)
    def _load_packages(self):
        self.call_from_thread(self._set_status, "Loading packages...")
        pkgs = get_all_packages()
        pkgs.sort(key=lambda p: p["name"].lower())
        self.call_from_thread(self._on_packages_loaded, pkgs)

    def _on_packages_loaded(self, pkgs):
        self._packages = pkgs
        self._checked.clear()
        filter_text = self.query_one("#filter-input", Input).value.lower()
        self._apply_filter(filter_text)
        self._set_status(f"Loaded {len(pkgs)} packages.")

    def _apply_filter(self, text: str):
        self._filtered = (
            [p for p in self._packages if text in p["name"].lower()]
            if text else list(self._packages)
        )
        self._checked.clear()
        self._rebuild_table()

    def _rebuild_table(self):
        table = self.query_one("#pkg-table", DataTable)
        table.clear()
        src_colors = {
            "pacman": "#a78bfa", "dnf": "#60a5fa", "apt": "#f97316",
            "zypper": "#34d399", "flatpak": "#fb7185"
        }
        for i, pkg in enumerate(self._filtered):
            checked = "[X]" if i in self._checked else "[ ]"
            src = pkg["source"]
            table.add_row(
                Text(checked, style="bold #3fb950" if i in self._checked else "#4b5563"),
                pkg["name"],
                Text(src, style=f"bold {src_colors.get(src, '#8b949e')}"),
                key=str(i)
            )
        sel = len(self._checked)
        self.query_one("#pkg-count", Label).update(
            f"[#3fb950]{len(self._filtered)}[/] packages\n[#f59e0b]{sel}[/] selected"
            if sel else f"[#3fb950]{len(self._filtered)}[/] packages"
        )

    def _set_status(self, msg: str):
        self.query_one("#status-bar", Label).update(msg)

    # ── Events ────────────────────────────────────────────────────────────────

    @on(Input.Changed, "#filter-input")
    def on_filter_changed(self, event: Input.Changed):
        self._apply_filter(event.value.lower())

    @on(DataTable.RowSelected, "#pkg-table")
    def on_row_selected(self, event: DataTable.RowSelected):
        idx = int(event.row_key.value)
        if idx in self._checked:
            self._checked.discard(idx)
        else:
            self._checked.add(idx)
        self._rebuild_table()
        try:
            self.query_one("#pkg-table", DataTable).move_cursor(row=event.cursor_row)
        except Exception:
            pass

    @on(Button.Pressed, "#btn-refresh")
    def action_refresh(self):
        self._set_status("Refreshing...")
        self._load_packages()

    @on(Button.Pressed, "#btn-exit")
    def on_exit_btn(self): self.exit()

    @on(Button.Pressed, "#btn-remove")
    def action_remove_selected(self):
        if not self._checked:
            self.push_screen(NotifyScreen("No packages selected.", success=False))
            return

        selected_pkgs = [self._filtered[i] for i in sorted(self._checked)]
        names = ", ".join(p["name"] for p in selected_pkgs[:3])
        if len(selected_pkgs) > 3:
            names += f" ... and {len(selected_pkgs) - 3} more"

        def on_confirmed(confirmed):
            if confirmed:
                self._do_remove(selected_pkgs)

        self.push_screen(
            ConfirmScreen(
                "Remove packages?",
                f"Do you really want to remove:\n{names}\n\nThis will uninstall the selected package(s)."
            ),
            callback=on_confirmed
        )

    @work(thread=True)
    def _do_remove(self, selected_pkgs):
        self.call_from_thread(self._set_status, f"Removing {len(selected_pkgs)} package(s)...")
        failed = []
        removed = []

        for pkg in selected_pkgs:
            identifier = pkg.get("app_id", pkg["name"]) if pkg["source"] == "flatpak" else pkg["name"]
            ok = remove_package(identifier, pkg["source"])
            if ok:
                removed.append((pkg["name"], pkg["source"]))
            else:
                failed.append(pkg["name"])

        if failed:
            msg = f"Removed {len(removed)}, failed {len(failed)}:\n" + ", ".join(failed)
            self.call_from_thread(self.push_screen, NotifyScreen(msg, success=False))
        else:
            self.call_from_thread(
                self.push_screen,
                NotifyScreen(f"Successfully removed {len(removed)} package(s).")
            )

        self.call_from_thread(self._show_next_leftovers, removed, 0)

    def _show_next_leftovers(self, removed: list[tuple], idx: int):
        if idx >= len(removed):
            self.action_refresh()
            return
        name, source = removed[idx]
        leftovers = leftover_searcher(name, source)
        if leftovers:
            def on_closed(_):
                self._show_next_leftovers(removed, idx + 1)
            self.push_screen(LeftoverScreen(name, leftovers), callback=on_closed)
        else:
            self._show_next_leftovers(removed, idx + 1)

    def action_select_all(self):
        if len(self._checked) == len(self._filtered):
            self._checked.clear()
        else:
            self._checked = set(range(len(self._filtered)))
        self._rebuild_table()


def main():
    app = LinuxSweep()
    app.run()

if __name__ == "__main__":
    main()

