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
    StaticText,
    TE_MULTILINE,
    TE_READONLY,
    TextCtrl,
    VERTICAL,
)

DISABLED_LABEL = "Start"
ENABLED_LABEL = "Stop"


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
        width = 512
        height = 384
        self.SetTitle("Save Game Backup Tool")
        if platform != "darwin":
            self.SetIcon(Icon(apply_working_directory("./BackupTool.ico")))
        self.panel = Panel(self, ID_ANY)
        sizer = BoxSizer(VERTICAL)
        grid = GridSizer(len(self.configs), 2, 0, 0)
        sizer.Add(grid, 0, EXPAND, 0)
        labels = []
        self.buttons = []
        button_grid_height = 0
        index = 0
        for config in self.configs:
            self.buttons.append(Button(self.panel, index, DISABLED_LABEL))
            labels.append(
                StaticText(self.panel, index, config["title"].replace("&", "&&"))
            )
            grid.Add(labels[len(labels) - 1], 0, ALIGN_CENTER, 0)
            grid.Add(self.buttons[len(self.buttons) - 1], 0, ALIGN_CENTER, 0)
            button_grid_height += (
                self.buttons[len(self.buttons) - 1].GetSize().GetHeight()
            )
            index += 1
        self.text_ctrl = TextCtrl(
            self.panel, ID_ANY, "", style=TE_MULTILINE | TE_READONLY
        )
        sizer.Add(self.text_ctrl, 2, ALL | EXPAND | FIXED_MINSIZE, 0)
        self.panel.SetSizer(sizer)
        if button_grid_height >= 0.75 * height:
            self.SetSize((width, int(button_grid_height + height * 2 / 3)))
        else:
            self.SetSize((width, height))
        self.SetMinSize(self.GetSize())
        self.Layout()
        self.Centre()
        for button in self.buttons:
            button.Bind(EVT_BUTTON, self.handle_button)
        self.Bind(EVT_CLOSE, self.on_close)

    def handle_button(self, event):
        index = event.GetEventObject().GetId()
        if self.configs[index].get("in_use") is None:
            add_config(self, self.configs[index], self.interval, self.text_ctrl)
            self.buttons[index].SetLabel(ENABLED_LABEL)
        else:
            self.remove_config(self.configs[index])

    def remove_config(self, config):
        self.buttons[self.configs.index(config)].SetLabel(DISABLED_LABEL)
        remove_config(config, self.stop_queue, self.backup_configs)

    def on_close(self, event):
        stop_backup_tool(self.stop_queue, self.backup_configs)
        self.Destroy()
