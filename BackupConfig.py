from __future__ import absolute_import
import os
import sys
import time
import wx
from BackupWatchdog import BackupWatchdog

class BackupConfig(object):
    def __init__(self, name=None, path=None, use_prompt=False, interval=0):
        if name is None: return
        self.name = name
        self.config_path = path
        self.stop_backup_file = backup_watchdog.replace_local_dot_directory(u"./.stop" + self.config_path.replace(u".json", u""))
        self.stop = False
        self.use_prompt = use_prompt
        self.interval = interval
        self.first_run = True

    def watchdog(self, stop_queue, text_ctrl=None, button_config=None, button_index=None):
        if self.config_path is not None:
            while not os.path.exists(self.stop_backup_file) and self.name not in stop_queue:
                time.sleep(self.interval)
                if backup_watchdog.watchdog(self.config_path, text_ctrl, button_config, button_index, self.use_prompt, self.first_run): break
                self.first_run = False
            self.stop = True
            self.first_run = True
            if os.path.exists(self.stop_backup_file):
                if text_ctrl is None:
                     if button_index is not None: button_config.remove_config(button_index, False)
                else: wx.CallAfter(button_config.remove_config, button_index)
            while os.path.exists(self.stop_backup_file):
                try: os.remove(self.stop_backup_file)
                except: pass
            if button_index is None: sys.exit(0)

backup_watchdog = BackupWatchdog()
