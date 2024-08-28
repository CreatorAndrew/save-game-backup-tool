from __future__ import absolute_import
from __future__ import division
from backup_config import add_config, remove_config, stop_backup_tool
from backup_utils import apply_working_directory
from io import open
from json import load
from sys import platform
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

DISABLED_LABEL = "Start"
ENABLED_LABEL = "Stop"
HEIGHT = 384
WIDTH = 512


class BackupGUI(Frame):
    def __init__(self, *args, **kwds):
        data = load(open(apply_working_directory("./MasterConfig.json"), "r"))
        for config in data["configurations"]:
            if config.get("in_use") is not None:
                del config["in_use"]
        self.backup_threads = []
        self.backup_configs = {}
        self.configs = data["configurations"]
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
        scroll_pane.SetScrollbars(1, 1, 100, 100)
        scroll_pane.SetSizer(grid)
        labels = []
        self.buttons = []
        index = 0
        for config in self.configs:
            self.buttons.append(Button(scroll_pane, index, DISABLED_LABEL))
            labels.append(
                StaticText(scroll_pane, index, config["title"].replace("&", "&&"))
            )
            grid.Add(labels[len(labels) - 1], 0, ALIGN_CENTER, 0)
            grid.Add(self.buttons[len(self.buttons) - 1], 0, ALIGN_CENTER, 0)
            grid_height += self.buttons[len(self.buttons) - 1].GetSize().GetHeight()
            index += 1
        max_grid_height = 5 * int(grid_height / (len(labels) if labels else 1))
        scroll_pane.SetSize(
            0, max_grid_height if grid_height > max_grid_height else grid_height
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
        for button in self.buttons:
            button.Bind(EVT_BUTTON, self.handle_button)
        self.Bind(EVT_CLOSE, self.on_close)

    def handle_button(self, event):
        index = event.GetEventObject().GetId()
        if self.configs[index].get("in_use") is None:
            self.buttons[index].SetLabel(ENABLED_LABEL)
            add_config(self, self.configs[index], self.interval, self.text_ctrl)
        else:
            self.remove_config(self.configs[index])

    def remove_config(self, config):
        self.buttons[self.configs.index(config)].SetLabel(DISABLED_LABEL)
        remove_config(config, self.stop_queue, self.backup_configs)

    def on_close(self, event):
        stop_backup_tool(self.stop_queue, self.backup_configs)
        self.Destroy()
