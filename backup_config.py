from __future__ import absolute_import
from os import listdir, remove
from time import sleep
from threading import Thread
from wx import CallAfter
from backup_utils import apply_working_directory, get_files_in_lower_case
from backup_watchdog import watchdog


def add_config(backup_tool, config, interval, text_ctrl=None):
    backup_tool.configs_used.append(config["uuid"])
    backup_tool.backup_configs[config["uuid"]] = BackupConfig(
        config["name"], config["uuid"], interval, True
    )
    backup_tool.backup_threads.append(
        Thread(
            target=backup_tool.backup_configs[config["uuid"]].watchdog,
            args=(backup_tool, config, text_ctrl),
        )
    )
    backup_tool.backup_threads[len(backup_tool.backup_threads) - 1].start()


def remove_all_configs(backup_tool, text_ctrl=None):
    for uuid in backup_tool.backup_configs.copy().keys():
        if text_ctrl is None:
            backup_tool.remove_config({"uuid": uuid})
        else:
            CallAfter(backup_tool.remove_config, {"uuid": uuid})


def remove_config(config, backup_configs, configs_used, stop_queue):
    stop_queue.append(config["uuid"])
    while backup_configs[config["uuid"]].continue_running:
        pass
    configs_used.remove(config["uuid"])
    stop_queue.remove(config["uuid"])
    del backup_configs[config["uuid"]]


class BackupConfig:
    def __init__(self, file, uuid, interval, use_prompt=False):
        self.config_file = file
        self.continue_running = True
        self.first_run = True
        self.interval = interval
        self.stop_backup_file = (
            ".stop"
            + file[
                : (
                    file.lower().rindex(".json")
                    if file.lower().endswith(".json")
                    else None
                )
            ]
        ).lower()
        self.use_prompt = use_prompt
        self.uuid = uuid

    def watchdog(self, backup_tool, config=None, text_ctrl=None):
        if self.config_file is not None:
            while self.uuid not in backup_tool.stop_queue and self.continue_running:
                sleep(self.interval)
                if watchdog(
                    self.config_file, text_ctrl, self.use_prompt, self.first_run
                ) or self.stop_backup_file in get_files_in_lower_case(
                    apply_working_directory(".")
                ):
                    while self.stop_backup_file in get_files_in_lower_case(
                        apply_working_directory(".")
                    ):
                        for file in listdir(apply_working_directory(".")):
                            if file.lower() == self.stop_backup_file:
                                try:
                                    remove(apply_working_directory("./" + file))
                                except:
                                    pass
                    self.continue_running = False
                    if text_ctrl is None:
                        if config is not None:
                            backup_tool.remove_config(config)
                    else:
                        CallAfter(backup_tool.remove_config, config)
                self.first_run = False
            self.first_run = True
            self.continue_running = False
