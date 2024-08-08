from backup_utils import apply_working_directory
from backup_watchdog import watchdog
from os import remove
from os.path import exists
from time import sleep
from wx import CallAfter


class BackupConfig:
    def __init__(self, name, path, interval, use_prompt=False):
        self.name = name
        self.config_path = path
        self.interval = interval
        self.use_prompt = use_prompt
        self.stop_backup_file = apply_working_directory(
            "./.stop"
            + path[
                : (
                    path.lower().rindex(".json")
                    if path.lower().endswith(".json")
                    else None
                )
            ]
        )
        self.continue_running = True
        self.first_run = True

    def watchdog(
        self, stop_queue, text_ctrl=None, button_config=None, button_index=None
    ):
        if self.config_path is not None:
            while self.name not in stop_queue and self.continue_running:
                sleep(self.interval)
                if watchdog(
                    self.config_path, text_ctrl, self.use_prompt, self.first_run
                ) or exists(self.stop_backup_file):
                    while exists(self.stop_backup_file):
                        try:
                            remove(self.stop_backup_file)
                        except:
                            pass
                    self.continue_running = False
                    if text_ctrl is None:
                        if button_index is not None:
                            button_config.remove_config(button_index, False)
                    else:
                        CallAfter(button_config.remove_config, button_index)
                self.first_run = False
            self.first_run = True
            self.continue_running = False
