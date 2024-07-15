from __future__ import absolute_import
from __future__ import print_function
from backup_config import BackupConfig
from backup_gui import BackupGUI
from backup_utils import apply_working_directory, PROMPT
from io import open
from pathlib2 import Path
from temp_history import TempHistory
from json import load
from os import chmod, getenv, remove, stat, system
from os.path import exists
from sys import argv, platform
from threading import Thread
from wx import App, ID_ANY

if platform != "darwin":
    from shutil import copy, move
if platform == "win32":
    from winshell import CreateShortcut


class BackupTool(App):
    def main(self):
        if platform == "darwin":
            system("clear")
        if platform == "linux" and exists(
            apply_working_directory("./.BackupTool.desktop")
        ):
            copy(
                apply_working_directory("./.BackupTool.desktop"),
                apply_working_directory("./BackupTool.desktop"),
            )
            lines = open(
                apply_working_directory("./BackupTool.desktop"), "r"
            ).readlines()
            for line in lines:
                if line.startswith("Exec="):
                    lines[lines.index(line)] = line = (
                        'Exec="'
                        + apply_working_directory(line.replace("Exec=", "")).replace(
                            "\n", '"\n'
                        )
                    )
                elif line.startswith("Icon="):
                    lines[lines.index(line)] = line = "Icon=" + apply_working_directory(
                        line.replace("Icon=", "")
                    )
            open(apply_working_directory("./BackupTool.desktop"), "w").writelines(lines)
            chmod(
                apply_working_directory("./BackupTool.desktop"),
                stat(apply_working_directory("./BackupTool.desktop")).st_mode | 0111,
            )
            try:
                remove(
                    str(Path.home()) + "/.local/share/applications/BackupTool.desktop"
                )
            except:
                pass
            move(
                apply_working_directory("./BackupTool.desktop"),
                str(Path.home()) + "/.local/share/applications",
            )
        if platform == "win32":
            CreateShortcut(
                Path=apply_working_directory("./Save Game Backup Tool.lnk"),
                Target=apply_working_directory("./BackupTool.exe"),
                Icon=(
                    apply_working_directory("./BackupTool.exe"),
                    0,
                ),
            )
            try:
                remove(
                    apply_working_directory(getenv("APPDATA"))
                    + "/Microsoft/Windows/Start Menu/Programs/Save Game Backup Tool.lnk"
                )
            except:
                try:
                    remove(
                        apply_working_directory(str(Path.home()))
                        + "/Start Menu/Programs/Save Game Backup Tool.lnk"
                    )
                except:
                    pass
            try:
                move(
                    apply_working_directory("./Save Game Backup Tool.lnk"),
                    apply_working_directory(getenv("APPDATA"))
                    + "/Microsoft/Windows/Start Menu/Programs",
                )
            except:
                move(
                    apply_working_directory("./Save Game Backup Tool.lnk"),
                    apply_working_directory(str(Path.home())) + "/Start Menu/Programs",
                )
        data = load(open(apply_working_directory("./MasterConfig.json"), "r"))
        self.backup_threads = []
        self.backup_configs = []
        self.configs_used = []
        config_path = None
        skip_choice = False
        no_gui = False
        for arg in argv:
            if arg.lower() == "--no-gui":
                no_gui = True
            elif arg.lower() == "--skip-choice":
                skip_choice = True
        if skip_choice:
            for config in data["configurations"]:
                if config["name"] == data["default"]:
                    config_path = config["file"]
        index = 0
        while index < len(argv) and not skip_choice:
            if argv[index].lower() == "--config" and index < len(argv) - 1:
                config_path = argv[index + 1].replace(".json", "") + ".json"
                break
            index += 1
        if no_gui:
            try:
                interval = data["interval"]
            except:
                interval = 0
            self.stop_queue = []
            continue_running = True
            if config_path is None:
                print('Enter in "help" or "?" for assistance.')
                while continue_running:
                    print(PROMPT, end="")
                    choice = input()
                    if choice == "start":
                        config = self.add_or_remove_config(
                            config_path, data["configurations"]
                        )
                        if config in self.configs_used:
                            print("That configuration is already in use.")
                        else:
                            self.configs_used.append(config)
                            self.backup_configs.append(
                                BackupConfig(
                                    config["name"], config["file"], interval, True
                                )
                            )
                            self.backup_threads.append(
                                Thread(
                                    target=self.backup_configs[
                                        len(self.backup_configs) - 1
                                    ].watchdog,
                                    args=(self.stop_queue, None, self, config),
                                )
                            )
                            self.backup_threads[len(self.backup_threads) - 1].start()
                    elif choice == "stop":
                        config = self.add_or_remove_config(
                            config_path, data["configurations"]
                        )
                        self.remove_config(config)
                    elif choice == "end" or choice == "exit" or choice == "quit":
                        for backup_config in self.backup_configs:
                            self.stop_queue.append(backup_config.name)
                            while backup_config.continue_running:
                                pass
                        self.stop_queue = []
                        self.backup_configs = []
                        self.configs_used = []
                        continue_running = False
                    elif choice == "help" or choice == "?":
                        print(
                            'Enter in "start" to initialize a backup configuration.\n'
                            + 'Enter in "stop" to suspend a backup configuration.\n'
                            + 'Enter in "end", "exit", or "quit" to shut down this tool.'
                        )
                    elif choice != "":
                        print("Invalid command")
            else:
                self.backup_configs.append(
                    BackupConfig(data["default"], config_path, interval)
                )
                self.backup_threads.append(
                    Thread(
                        target=self.backup_configs[0].watchdog, args=(self.stop_queue,)
                    )
                )
                self.backup_threads[0].start()
        else:
            app = App()
            frame = BackupGUI(None, ID_ANY, "")
            frame.Show()
            app.MainLoop()

    def remove_config(self, config, wait=True):
        if config in self.configs_used:
            self.stop_queue.append(
                self.backup_configs[self.configs_used.index(config)].name
            )
            while (
                wait
                and self.backup_configs[
                    self.configs_used.index(config)
                ].continue_running
            ):
                pass
            self.stop_queue.remove(
                self.backup_configs[self.configs_used.index(config)].name
            )
            self.backup_configs.remove(
                self.backup_configs[self.configs_used.index(config)]
            )
            self.configs_used.remove(config)
        else:
            print("That configuration was not in use.")

    def add_or_remove_config(self, config_path, configs):
        if config_path is None:
            print("Select one of the following configurations:")
            index = 0
            for config in configs:
                print("    " + str(index) + ": " + config["name"])
                index += 1
            choice = None
            while choice is None:
                try:
                    print("Enter in an option number here: ", end="")
                    choice = int(input())
                    if choice >= len(configs) or choice < 0:
                        print("Not a valid option number. Try again.")
                        choice = None
                except ValueError:
                    print("Invalid input value. Try again with a numeric value.")
                    choice = None
            config = configs[choice]
        return config


temp_history = TempHistory()
print = temp_history.print
input = temp_history.input
backup_tool = BackupTool()
backup_tool.main()
