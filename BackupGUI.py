from __future__ import division
from __future__ import absolute_import
import threading
import wx
from BackupConfig import BackupConfig

class BackupGUI(wx.Frame):
    def __init__(self, *args, **kwds):
        kwds[u"style"] = kwds.get(u"style", 0) | wx.DEFAULT_FRAME_STYLE
        wx.Frame.__init__(self, *args, **kwds)
        width = 512
        height = 384
        self.SetTitle(u"Save Game Backup Tool")

        self.panel = wx.Panel(self, wx.ID_ANY)

        sizer = wx.BoxSizer(wx.VERTICAL)
        grid = wx.GridSizer(len(configs), 2, 0, 0)
        sizer.Add(grid, 0, wx.EXPAND, 0)

        labels = []
        self.buttons = []
        index = 0
        button_grid_height = 0
        for config in configs:
            self.buttons.append(wx.Button(self.panel, index, u"Start"))
            labels.append(wx.StaticText(self.panel, index, configs[configs.index(config)][u"name"].replace(u"&", u"&&")))
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
        if configs[index] not in configs_used:
            configs_used.append(configs[index])
            backup_configs.append(BackupConfig(name=configs[index][u"name"], path=configs[index][u"file"]))
            backup_threads.append(threading.Thread(target=backup_configs[len(backup_configs) - 1].watchdog,
                                                   args=(stop_queue, self.text_ctrl, self, index)))
            backup_threads[len(backup_threads) - 1].start()
            self.buttons[index].SetLabel(u"Stop")
        else: self.remove_config(index)

    def remove_config(self, index, join=True):
        stop_queue.append(backup_configs[configs_used.index(configs[index])].name)
        if join: backup_threads[configs_used.index(configs[index])].join()
        while not backup_configs[configs_used.index(configs[index])].stop: pass
        stop_queue.remove(backup_configs[configs_used.index(configs[index])].name)
        backup_configs.remove(backup_configs[configs_used.index(configs[index])])
        configs_used.remove(configs_used[configs_used.index(configs[index])])
        self.buttons[index].SetLabel(u"Start")

    def on_close(self, event):
        try:
            index = 0
            while index < len(configs_used):
                stop_queue.append(backup_configs[configs_used.index(configs[index])].name)
                backup_threads[configs_used.index(configs[index])].join()
                while not backup_configs[configs_used.index(configs[index])].stop: pass
                index += 1
        except Exception: pass
        backup_configs = []
        configs_used = []
        stop_queue = []
        self.Destroy()

backup_threads = []
backup_configs = []
backup_config = BackupConfig()
configs = backup_config.get_configs()
configs_used = []
stop_queue = []
