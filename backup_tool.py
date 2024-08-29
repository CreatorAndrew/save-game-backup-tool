from __future__ import absolute_import
from __future__ import print_function
from io import open
from json import load
from os import listdir
from sys import argv, platform
from threading import Thread
from uuid import uuid4
from wx import App, ID_ANY
from backup_config import add_config, BackupConfig, remove_config, stop_backup_tool
from backup_gui import BackupGUI
from backup_utils import apply_working_directory, PROMPT
from temp_history import TempHistory

try:
    from pathlib import Path
except:
    from pathlib2 import Path


class BackupTool(App):
    def main(self):
        data = load(open(apply_working_directory("./MasterConfig.json"), "r"))
        if platform == "darwin":
            from os import system

            system("clear")
        elif data.get("createShortcut") is not None and data["createShortcut"]:
            if platform == "linux":
                from os import chmod, stat

                shortcut_path = (
                    str(Path.home()) + "/.local/share/applications/BackupTool.desktop"
                )
                open(shortcut_path, "w").writelines(
                    [
                        "[Desktop Entry]\n",
                        "Type=Application\n",
                        "Categories=Game;Utility\n",
                        "Name=Save Game Backup Tool\n",
                        'Exec="' + apply_working_directory("./BackupTool") + '"\n',
                        "Icon=" + apply_working_directory("./BackupTool.ico") + "\n",
                    ]
                )
                chmod(shortcut_path, stat(shortcut_path).st_mode | 0o0111)
            if platform == "win32":
                from os import getenv
                from winshell import CreateShortcut

                def create_shortcut_at(shortcut_path):
                    CreateShortcut(
                        Path=shortcut_path,
                        Target=apply_working_directory("./BackupTool.exe"),
                        Icon=(apply_working_directory("./BackupTool.exe"), 0),
                    )

                try:
                    create_shortcut_at(
                        getenv("APPDATA")
                        + "/Microsoft/Windows/Start Menu/Programs/Save Game Backup Tool.lnk"
                    )
                except:
                    create_shortcut_at(
                        str(Path.home())
                        + "/Start Menu/Programs/Save Game Backup Tool.lnk"
                    )
        self.backup_configs = {}
        self.backup_threads = []
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
            config_path = data["default"]
        index = 0
        while index < len(argv) and not skip_choice:
            if argv[index].lower() == "--config" and index < len(argv) - 1:
                for file in listdir(apply_working_directory(".")):
                    if (
                        file.lower().endswith(".json")
                        and file.lower()
                        == argv[index + 1].lower().replace(".json", "") + ".json"
                    ):
                        config_path = file
                        break
                break
            index += 1
        if no_gui:
            for config in data["configurations"]:
                config["uuid"] = uuid4()
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
                    if choice in ["start"]:
                        config = add_or_remove_config(data["configurations"])
                        if config["uuid"] in self.configs_used:
                            print("That configuration is already in use.")
                        else:
                            add_config(self, config, interval)
                    elif choice in ["stop"]:
                        config = add_or_remove_config(data["configurations"])
                        if config["uuid"] in self.configs_used:
                            self.remove_config(config)
                        else:
                            print("That configuration was not in use.")
                    elif choice in ["end", "exit", "quit"]:
                        stop_backup_tool(
                            self.backup_configs, self.configs_used, self.stop_queue
                        )
                        continue_running = False
                    elif choice in ["help", "?"]:
                        print(
                            'Enter in "start" to initialize a backup configuration.\n'
                            + 'Enter in "stop" to suspend a backup configuration.\n'
                            + 'Enter in "end", "exit", or "quit" to shut down this tool.'
                        )
                    elif choice:
                        print("Invalid command")
            else:
                self.backup_configs[config_path] = BackupConfig(config_path, interval)
                self.backup_threads.append(
                    Thread(
                        target=self.backup_configs[config_path].watchdog, args=(self,)
                    )
                )
                self.backup_threads[0].start()
        else:
            app = App()
            frame = BackupGUI(None, ID_ANY, "")
            frame.Show()
            app.MainLoop()

    def remove_config(self, config):
        remove_config(config, self.backup_configs, self.configs_used, self.stop_queue)


def add_or_remove_config(configs):
    print("Select one of the following configurations:")
    index = 0
    for config in configs:
        print("    " + str(index) + ": " + config["title"])
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
