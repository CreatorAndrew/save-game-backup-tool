from __future__ import absolute_import
from backup_utils import apply_working_directory, get_files_in_lower_case
from backup_watchdog import watchdog
from os import remove
from os.path import basename
from time import sleep
from threading import Thread
from wx import CallAfter


def add_config(callback, config, interval, text_ctrl=None):
    config["in_use"] = True
    callback.backup_configs[config["name"]] = BackupConfig(
        config["name"], interval, True
    )
    callback.backup_threads.append(
        Thread(
            target=callback.backup_configs[config["name"]].watchdog,
            args=(callback, config, text_ctrl),
        )
    )
    callback.backup_threads[len(callback.backup_threads) - 1].start()


def remove_config(config, stop_queue, backup_configs):
    stop_queue.append(config["name"])
    while backup_configs[config["name"]].continue_running:
        pass
    stop_queue.remove(config["name"])
    del backup_configs[config["name"]]
    del config["in_use"]


def stop_backup_tool(stop_queue, backup_configs):
    for backup_config in backup_configs.items():
        stop_queue.append(backup_config[0])
        while backup_config[1].continue_running:
            pass
    stop_queue = []
    backup_configs = {}


class BackupConfig:
    def __init__(self, path, interval, use_prompt=False):
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

    def watchdog(self, callback, config=None, text_ctrl=None):
        if self.config_path is not None:
            while self.config_path not in callback.stop_queue and self.continue_running:
                sleep(self.interval)
                if watchdog(
                    self.config_path, text_ctrl, self.use_prompt, self.first_run
                ) or basename(self.stop_backup_file).lower() in get_files_in_lower_case(
                    apply_working_directory(".")
                ):
                    while basename(
                        self.stop_backup_file
                    ).lower() in get_files_in_lower_case(apply_working_directory(".")):
                        try:
                            remove(self.stop_backup_file)
                        except:
                            pass
                    self.continue_running = False
                    if text_ctrl is None:
                        if config is not None:
                            callback.remove_config(config)
                    else:
                        CallAfter(callback.remove_config, config)
                self.first_run = False
            self.first_run = True
            self.continue_running = False
