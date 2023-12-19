from __future__ import absolute_import
from __future__ import division
from BackupConfig import BackupConfig
from BackupWatchdog import BackupWatchdog
import json
import sys
import threading
import wx

class BackupGUI(wx.Frame):
    def __init__(self, *args, **kwds):
        data = json.load(open(BackupWatchdog().replace_local_dot_directory(u"./MasterConfig.json"), u"r"))

        self.backup_configs = []
        self.backup_threads = []
        self.configs = data[u"configurations"]
        self.configs_used = []
        self.stop_queue = []
        try: self.interval = data[u"interval"]
        except: self.interval = 0

        kwds[u"style"] = kwds.get(u"style", 0) | wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwds)
        width = 512
        height = 384
        self.SetTitle(u"Save Game Backup Tool")
        if sys.platform != u"darwin": self.SetIcon(wx.Icon(BackupWatchdog().replace_local_dot_directory(u"./BackupTool.ico")))
        self.panel = wx.Panel(self, wx.ID_ANY)
        sizer = wx.BoxSizer(wx.VERTICAL)
        grid = wx.GridSizer(len(self.configs), 2, 0, 0)
        sizer.Add(grid, 0, wx.EXPAND, 0)

        labels = []
        self.buttons = []
        index = 0
        button_grid_height = 0
        for config in self.configs:
            self.buttons.append(wx.Button(self.panel, index, u"Start"))
            labels.append(wx.StaticText(self.panel, index, self.configs[self.configs.index(config)][u"name"].replace(u"&", u"&&")))
            grid.Add(labels[len(labels) - 1], 0, wx.ALIGN_CENTER, 0)
            grid.Add(self.buttons[len(self.buttons) - 1], 0, wx.ALIGN_CENTER, 0)
            button_grid_height += self.buttons[len(self.buttons) - 1].GetSize().GetHeight()
            index += 1

        self.text_ctrl = wx.TextCtrl(self.panel, wx.ID_ANY, u"", style=wx.TE_MULTILINE | wx.TE_READONLY)
        sizer.Add(self.text_ctrl, 2, wx.ALL | wx.EXPAND | wx.FIXED_MINSIZE, 0)
        self.panel.SetSizer(sizer)
        if button_grid_height >= 0.75 * height: self.SetSize((width, int(button_grid_height + height * 2 / 3)))
        else: self.SetSize((width, height))
        self.SetMinSize(self.GetSize())
        self.Layout()
        self.Centre()

        for button in self.buttons: button.Bind(wx.EVT_BUTTON, self.handle_button)
        self.Bind(wx.EVT_CLOSE, self.on_close)

    def handle_button(self, event):
        index = event.GetEventObject().GetId()
        if self.configs[index] not in self.configs_used:
            self.configs_used.append(self.configs[index])
            self.backup_configs.append(BackupConfig(self.configs[index][u"name"], self.configs[index][u"file"], self.interval))
            self.backup_threads.append(threading.Thread(target=self.backup_configs[len(self.backup_configs) - 1].watchdog,
                                                        args=(self.stop_queue, self.text_ctrl, self, index)))
            self.backup_threads[len(self.backup_threads) - 1].start()
            self.buttons[index].SetLabel(u"Stop")
        else: self.remove_config(index)

    def remove_config(self, index):
        self.buttons[index].SetLabel(u"Start")
        self.stop_queue.append(self.backup_configs[self.configs_used.index(self.configs[index])].name)
        while not self.backup_configs[self.configs_used.index(self.configs[index])].stop: pass
        self.stop_queue.remove(self.backup_configs[self.configs_used.index(self.configs[index])].name)
        self.backup_configs.remove(self.backup_configs[self.configs_used.index(self.configs[index])])
        self.configs_used.remove(self.configs_used[self.configs_used.index(self.configs[index])])

    def on_close(self, event):
        for backup_config in self.backup_configs:
            self.stop_queue.append(backup_config.name)
            while not backup_config.stop: pass
        self.stop_queue = []
        self.backup_configs = []
        self.configs_used = []
        self.Destroy()
