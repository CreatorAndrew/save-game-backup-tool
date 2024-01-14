from BackupWatchdog import BackupWatchdog
import os
import time
import wx

class BackupConfig:
    def __init__(self, name, path, interval, use_prompt=False):
        self.name = name
        self.config_path = path
        self.interval = interval
        self.use_prompt = use_prompt
        self.stop_backup_file = BackupWatchdog().replace_local_dot_directory("./.stop" + self.config_path.replace(".json", ""))
        self.stop = False
        self.first_run = True

    def watchdog(self, stop_queue, text_ctrl=None, button_config=None, button_index=None):
        if self.config_path is not None:
            while self.name not in stop_queue and not self.stop:
                time.sleep(self.interval)
                if BackupWatchdog().watchdog(self.config_path, text_ctrl, self.use_prompt, self.first_run) or os.path.exists(self.stop_backup_file):
                    while os.path.exists(self.stop_backup_file):
                        try: os.remove(self.stop_backup_file)
                        except: pass
                    self.stop = True
                    if text_ctrl is None:
                        if button_index is not None: button_config.remove_config(button_index, False)
                    else: wx.CallAfter(button_config.remove_config, button_index)
                self.first_run = False
            self.first_run = True
            self.stop = True
