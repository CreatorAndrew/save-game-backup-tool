# pyright: reportMissingImports=false
from __future__ import absolute_import
from __future__ import division
from io import open
from json import load
from sys import platform
from uuid import uuid4
from wx import (
    ALIGN_CENTER,
    ALL,
    BoxSizer,
    Button,
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
from wx.adv import TaskBarIcon, EVT_TASKBAR_LEFT_UP
from backup_config import add_config, remove_all_configs, remove_config
from backup_utils import apply_working_directory

try:
    from AppKit import NSApp, NSApplication
except:
    pass

try:
    from gi import require_version

    require_version("Gtk", "3.0")
    from gi.repository import GObject, Gtk

    HAS_GTK = True
except:
    try:
        from PySide6.QtCore import QPoint
        from PySide6.QtGui import QAction, QIcon
        from PySide6.QtWidgets import QApplication, QMenu, QSystemTrayIcon

        HAS_QT = True
    except:
        from wx import EVT_MENU, Menu

        HAS_QT = False
    HAS_GTK = False

DISABLED_LABEL = "Start"
ENABLED_LABEL = "Stop"
EXIT_LABEL = "Exit"
HEIGHT = 384
HIDDEN_LABEL = "Show"
SHOWN_LABEL = "Hide"
TITLE = "Save Game Backup Tool"
TRAY_ICON_PATH = apply_working_directory(
    (
        "./Save Game Backup Tool.app/Contents/Resources/"
        if platform == "darwin"
        else "./"
    )
    + "BackupTool.ico"
)
WIDTH = 512


def go_foreground():
    try:
        NSApplication.sharedApplication()
        NSApp().activateIgnoringOtherApps_(True)
    except:
        pass


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
            self.hide_on_close = data["hideOnClose"]
        except:
            self.hide_on_close = False
        try:
            self.interval = data["interval"]
        except:
            self.interval = 0
        kwds["style"] = kwds.get("style", 0) | DEFAULT_FRAME_STYLE
        Frame.__init__(self, *args, **kwds)
        if not (HAS_GTK or HAS_QT):
            self.tray_icon = BackupTrayIcon(self)
        self.SetTitle(TITLE)
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
        self.Show(True if data.get("startHidden") is None else not data["startHidden"])

    def exit(self):
        remove_all_configs(self, self.text_ctrl)
        self.Hide()
        if not (HAS_GTK or HAS_QT):
            self.tray_icon.Destroy()
        self.Destroy()
        if HAS_GTK:
            GObject.timeout_add(int(self.interval * 1000), Gtk.main_quit)
        if HAS_QT:
            self.app.quit()

    def handle_button(self, event):
        config = self.configs[event.GetEventObject().GetId()]
        if config["uuid"] in self.configs_used:
            self.remove_config(config)
        else:
            self.buttons[config["uuid"]].SetLabel(ENABLED_LABEL)
            add_config(self, config, self.interval, self.text_ctrl)

    def on_close(self, _):
        if HAS_GTK or HAS_QT:
            self.toggle_shown_item.set_label(HIDDEN_LABEL)
        if self.hide_on_close:
            self.Hide()
        else:
            self.exit()

    def remove_config(self, config):
        self.buttons[config["uuid"]].SetLabel(DISABLED_LABEL)
        remove_config(config, self.backup_configs, self.configs_used, self.stop_queue)


class BackupToolGUI:
    def __init__(self, app):
        self.frame = BackupGUI(None, ID_ANY)
        if HAS_GTK:
            tray_icon = Gtk.StatusIcon()
            tray_icon.set_from_file(TRAY_ICON_PATH)
            tray_icon.set_tooltip_text(TITLE)
            tray_icon.set_visible(True)
            tray_icon.connect("activate", self.on_tray_toggle_shown)
            tray_icon.connect("popup-menu", self.on_tray_menu_popup)
            self.toggle_shown_item = Gtk.MenuItem(
                SHOWN_LABEL if self.frame.IsShown() else HIDDEN_LABEL
            )
            self.toggle_shown_item.connect("activate", self.on_tray_toggle_shown)
            exit_item = Gtk.MenuItem(EXIT_LABEL)
            exit_item.connect("activate", self.on_tray_exit)
            self.menu = Gtk.Menu()
            self.menu.append(self.toggle_shown_item)
            self.menu.append(exit_item)
            self.menu.show_all()
            self.frame.toggle_shown_item = self.toggle_shown_item
            Gtk.main()
            return
        if HAS_QT:
            self.frame.app = QApplication([])
            self.frame.app.setQuitOnLastWindowClosed(False)
            self.tray_icon = QSystemTrayIcon()
            self.tray_icon.setIcon(QIcon(TRAY_ICON_PATH))
            self.tray_icon.setToolTip(TITLE)
            self.tray_icon.setVisible(True)
            self.tray_icon.activated.connect(self.handle_tray_icon)
            self.toggle_shown_item = QAction(
                SHOWN_LABEL if self.frame.IsShown() else HIDDEN_LABEL
            )
            self.toggle_shown_item.triggered.connect(self.on_tray_toggle_shown)
            self.toggle_shown_item.set_label = self.toggle_shown_item.setText
            exit_item = QAction(EXIT_LABEL)
            exit_item.triggered.connect(self.on_tray_exit)
            self.menu = QMenu()
            self.menu.addAction(self.toggle_shown_item)
            self.menu.addAction(exit_item)
            self.frame.toggle_shown_item = self.toggle_shown_item
        app.MainLoop()

    def handle_tray_icon(self, reason):
        if reason == QSystemTrayIcon.Trigger:
            self.toggle_shown_item.setText(
                HIDDEN_LABEL if self.frame.IsShown() else SHOWN_LABEL
            )
            self.frame.Show(not self.frame.IsShown())
            go_foreground()
        if reason == QSystemTrayIcon.Context:
            point = QPoint()
            point.setX(self.tray_icon.geometry().x())
            point.setY(self.tray_icon.geometry().y())
            self.menu.popup(point)

    def on_tray_exit(self, _):
        self.frame.exit()

    def on_tray_menu_popup(self, _, button, time):
        self.menu.popup(None, None, None, None, button, time)

    def on_tray_toggle_shown(self, _):
        self.toggle_shown_item.set_label(
            HIDDEN_LABEL if self.frame.IsShown() else SHOWN_LABEL
        )
        self.frame.Show(not self.frame.IsShown())
        go_foreground()


class BackupTrayIcon(TaskBarIcon):
    def __init__(self, frame):
        TaskBarIcon.__init__(self)
        self.frame = frame
        self.SetIcon(Icon(TRAY_ICON_PATH), TITLE)
        self.Bind(EVT_MENU, self.on_tray_exit, id=1)
        self.Bind(EVT_MENU, self.on_tray_toggle_shown, id=2)
        self.Bind(EVT_TASKBAR_LEFT_UP, self.on_tray_toggle_shown)

    def build_menu(self):
        menu = Menu()
        menu.Append(2, SHOWN_LABEL if self.frame.IsShown() else HIDDEN_LABEL)
        menu.Append(1, EXIT_LABEL)
        return menu

    def CreatePopupMenu(self):
        return self.build_menu()

    def on_tray_exit(self, _):
        self.frame.exit()

    def on_tray_toggle_shown(self, _):
        self.frame.Show(not self.frame.IsShown())
        go_foreground()
