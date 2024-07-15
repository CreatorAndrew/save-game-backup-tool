from __future__ import absolute_import
from __future__ import division
from backup_config import BackupConfig
from backup_utils import apply_working_directory
from io import open
from json import load
from sys import platform
from threading import Thread
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


class BackupGUI(Frame):
    def __init__(self, *args, **kwds):
        data = load(
            open(
                apply_working_directory("./MasterConfig.json"), "r"
            )
        )
        self.backup_threads = []
        self.backup_configs = []
        self.configs = data["configurations"]
        self.configs_used = []
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
            self.SetIcon(
                Icon(
                    apply_working_directory("./BackupTool.ico")
                )
            )
        self.panel = Panel(self, ID_ANY)
        sizer = BoxSizer(VERTICAL)
        grid = GridSizer(len(self.configs), 2, 0, 0)
        sizer.Add(grid, 0, EXPAND, 0)
        labels = []
        self.buttons = []
        button_grid_height = 0
        index = 0
        while index < len(self.configs):
            self.buttons.append(Button(self.panel, index, "Start"))
            labels.append(
                StaticText(
                    self.panel, index, self.configs[index]["name"].replace("&", "&&")
                )
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
        if self.configs[index] in self.configs_used:
            self.remove_config(index)
        else:
            self.configs_used.append(self.configs[index])
            self.backup_configs.append(
                BackupConfig(
                    self.configs[index]["name"],
                    self.configs[index]["file"],
                    self.interval,
                )
            )
            self.backup_threads.append(
                Thread(
                    target=self.backup_configs[len(self.backup_configs) - 1].watchdog,
                    args=(self.stop_queue, self.text_ctrl, self, index),
                )
            )
            self.backup_threads[len(self.backup_threads) - 1].start()
            self.buttons[index].SetLabel("Stop")

    def remove_config(self, index):
        self.buttons[index].SetLabel("Start")
        self.stop_queue.append(
            self.backup_configs[self.configs_used.index(self.configs[index])].name
        )
        while self.backup_configs[
            self.configs_used.index(self.configs[index])
        ].continue_running:
            pass
        self.stop_queue.remove(
            self.backup_configs[self.configs_used.index(self.configs[index])].name
        )
        self.backup_configs.remove(
            self.backup_configs[self.configs_used.index(self.configs[index])]
        )
        self.configs_used.remove(
            self.configs_used[self.configs_used.index(self.configs[index])]
        )

    def on_close(self, event):
        for backup_config in self.backup_configs:
            self.stop_queue.append(backup_config.name)
            while backup_config.continue_running:
                pass
        self.stop_queue = []
        self.backup_configs = []
        self.configs_used = []
        self.Destroy()
