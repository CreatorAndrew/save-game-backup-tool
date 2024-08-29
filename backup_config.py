from __future__ import absolute_import
from os import listdir, remove
from os.path import basename
from time import sleep
from threading import Thread
from wx import CallAfter
from backup_utils import apply_working_directory, get_files_in_lower_case
from backup_watchdog import watchdog


def add_config(callback, config, interval, text_ctrl=None):
    callback.configs_used.append(config["uuid"])
    callback.backup_configs[config["uuid"]] = BackupConfig(
        config["name"], config["uuid"], interval, True
    )
    callback.backup_threads.append(
        Thread(
            target=callback.backup_configs[config["uuid"]].watchdog,
            args=(callback, config, text_ctrl),
        )
    )
    callback.backup_threads[len(callback.backup_threads) - 1].start()


def remove_config(config, backup_configs, configs_used, stop_queue):
    stop_queue.append(config["uuid"])
    while backup_configs[config["uuid"]].continue_running:
        pass
    configs_used.remove(config["uuid"])
    stop_queue.remove(config["uuid"])
    del backup_configs[config["uuid"]]


def stop_backup_tool(backup_configs, configs_used, stop_queue):
    for backup_config in backup_configs.copy().items():
        remove_config(
            {"uuid": backup_config[0]}, backup_configs, configs_used, stop_queue
        )


class BackupConfig:
    def __init__(self, path, uuid, interval, use_prompt=False):
        self.config_path = path
        self.continue_running = True
        self.first_run = True
        self.interval = interval
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
        self.use_prompt = use_prompt
        self.uuid = uuid

    def watchdog(self, callback, config=None, text_ctrl=None):
        if self.config_path is not None:
            while self.uuid not in callback.stop_queue and self.continue_running:
                sleep(self.interval)
                if watchdog(
                    self.config_path, text_ctrl, self.use_prompt, self.first_run
                ) or basename(self.stop_backup_file).lower() in get_files_in_lower_case(
                    apply_working_directory(".")
                ):
                    while basename(
                        self.stop_backup_file
                    ).lower() in get_files_in_lower_case(apply_working_directory(".")):
                        for file in listdir(apply_working_directory(".")):
                            if file.lower() == basename(self.stop_backup_file).lower():
                                try:
                                    remove(apply_working_directory("./" + file))
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
