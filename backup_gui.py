from __future__ import absolute_import
from __future__ import division
from gi import require_version

require_version("Gtk", "3.0")
require_version("AppIndicator3", "0.1")
from gi.repository import AppIndicator3, GObject, Gtk
from io import open
from json import load
from sys import platform
from uuid import uuid4
from wx import (
    ALIGN_CENTER,
    ALL,
    BoxSizer,
    Button,
    CallAfter,
    DEFAULT_FRAME_STYLE,
    EVT_BUTTON,
    EVT_CLOSE,
    EXPAND,
    FIXED_MINSIZE,
    Frame,
    GridSizer,
    Icon,
    ID_ANY,
    Panel,
    ScrolledWindow,
    StaticText,
    TE_MULTILINE,
    TE_READONLY,
    TextCtrl,
    VERTICAL,
)
from backup_config import add_config, remove_all_configs, remove_config
from backup_utils import apply_working_directory

APPINDICATOR_ID = "Save Game Backup Tool"
DISABLED_LABEL = "Start"
ENABLED_LABEL = "Stop"
HEIGHT = 384
HIDDEN_LABEL = "Show"
SHOWN_LABEL = "Hide"
WIDTH = 512


class BackupGUI(Frame):
    def __init__(self, *args, **kwds):
        data = load(open(apply_working_directory("./MasterConfig.json"), "r"))

        for config in data["configurations"]:
            config["uuid"] = uuid4()
        self.backup_configs = {}
        self.backup_threads = []
        self.configs = data["configurations"]
        self.configs_used = []
        self.stop_queue = []
        try:
            self.interval = data["interval"]
        except:
            self.interval = 0
        kwds["style"] = kwds.get("style", 0) | DEFAULT_FRAME_STYLE
        Frame.__init__(self, *args, **kwds)
        self.SetTitle("Save Game Backup Tool")
        if platform != "darwin":
            self.SetIcon(Icon(apply_working_directory("./BackupTool.ico")))
        panel = Panel(self, ID_ANY)
        sizer = BoxSizer(VERTICAL)
        grid = GridSizer(len(self.configs), 2, 0, 0)
        grid_height = 0
        scroll_pane = ScrolledWindow(panel, ID_ANY)
        scroll_pane.SetSizer(grid)
        self.buttons = {}
        labels = []
        for index, config in enumerate(self.configs):
            self.buttons[config["uuid"]] = Button(scroll_pane, index, DISABLED_LABEL)
            labels.append(
                StaticText(scroll_pane, index, config["title"].replace("&", "&&"))
            )
            grid.Add(labels[len(labels) - 1], 0, ALIGN_CENTER, 0)
            grid.Add(self.buttons[config["uuid"]], 0, ALIGN_CENTER, 0)
            grid_height += self.buttons[config["uuid"]].GetSize().GetHeight()
        button_height = int(grid_height / (len(labels) if labels else 1))
        scroll_pane.SetScrollbars(1, button_height, 100, 100)
        scroll_pane.SetSize(
            0, 5 * button_height if grid_height > 5 * button_height else grid_height
        )
        sizer.Add(scroll_pane, 0, EXPAND | FIXED_MINSIZE, 0)
        self.text_ctrl = TextCtrl(panel, ID_ANY, "", style=TE_MULTILINE | TE_READONLY)
        sizer.Add(self.text_ctrl, 2, ALL | EXPAND | FIXED_MINSIZE, 0)
        panel.SetSizer(sizer)
        try:
            self.SetSize(self.FromDIP(WIDTH, HEIGHT))
        except:
            self.SetSize(WIDTH, HEIGHT)
        self.SetMinSize(self.GetSize())
        self.Layout()
        self.Center()
        for button in self.buttons.values():
            button.Bind(EVT_BUTTON, self.handle_button)
        self.Bind(EVT_CLOSE, self.on_close)
        self.Show(
            True if data.get("startMinimized") is None else not data["startMinimized"]
        )

    def handle_button(self, event):
        config = self.configs[event.GetEventObject().GetId()]
        if config["uuid"] in self.configs_used:
            self.remove_config(config)
        else:
            self.buttons[config["uuid"]].SetLabel(ENABLED_LABEL)
            add_config(self, config, self.interval, self.text_ctrl)

    def on_close(self, event):
        self.toggle_shown_item.set_label(HIDDEN_LABEL)
        self.Hide()

    def exit(self):
        remove_all_configs(self, self.text_ctrl)
        self.Hide()
        self.Destroy()

    def remove_config(self, config):
        self.buttons[config["uuid"]].SetLabel(DISABLED_LABEL)
        remove_config(config, self.backup_configs, self.configs_used, self.stop_queue)


class BackupTrayIcon:
    def __init__(self):
        self.frame = BackupGUI(None, ID_ANY)
        indicator = AppIndicator3.Indicator.new(
            APPINDICATOR_ID,
            apply_working_directory(
                (
                    "./Save Game Backup Tool.app/Contents/Resources/"
                    if platform == "darwin"
                    else "./"
                )
                + "BackupTool.ico"
            ),
            AppIndicator3.IndicatorCategory.SYSTEM_SERVICES,
        )
        indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)
        indicator.set_menu(self.build_menu())
        self.frame.toggle_shown_item = self.toggle_shown_item
        Gtk.main()

    def build_menu(self):
        menu = Gtk.Menu()
        self.toggle_shown_item = Gtk.MenuItem(
            "Hide" if self.frame.IsShown() else "Show"
        )
        exit_item = Gtk.MenuItem("Exit")
        self.toggle_shown_item.connect("activate", self.on_tray_toggle_shown)
        exit_item.connect("activate", self.on_tray_exit)
        menu.append(self.toggle_shown_item)
        menu.append(exit_item)
        menu.show_all()
        return menu

    def on_tray_exit(self, _):
        timeout = self.frame.interval
        self.frame.exit()
        GObject.timeout_add(int(timeout * 1000), Gtk.main_quit)

    def on_tray_toggle_shown(self, _):
        if self.frame.IsShown():
            self.toggle_shown_item.set_label(HIDDEN_LABEL)
            self.frame.Hide()
        else:
            self.toggle_shown_item.set_label(SHOWN_LABEL)
            self.frame.Show()
