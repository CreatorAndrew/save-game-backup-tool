from BackupConfig import BackupConfig
from BackupGUI import BackupGUI
from BackupWatchdog import BackupWatchdog
from pathlib import Path
from TempHistory import TempHistory
import json
import os
import sys
import threading
import wx

if sys.platform != "darwin": import shutil
if sys.platform == "win32": import winshell
else: import subprocess

class BackupTool(wx.App):
    def main(self):
        if sys.platform == "darwin": subprocess.run("clear")
        if sys.platform == "linux" and os.path.exists(backup_watchdog.replace_local_dot_directory("./.BackupTool.desktop")):
            shutil.copy(backup_watchdog.replace_local_dot_directory("./.BackupTool.desktop"),
                        backup_watchdog.replace_local_dot_directory("./BackupTool.desktop"))
            lines = open(backup_watchdog.replace_local_dot_directory("./BackupTool.desktop"), "r").readlines()
            for line in lines:
                if line.startswith("Exec="):
                    lines[lines.index(line)] = line = "Exec=\"" + backup_watchdog.replace_local_dot_directory(line.replace("Exec=", "")).replace("\n", "\"\n")
                elif line.startswith("Icon="): lines[lines.index(line)] = line = "Icon=" + backup_watchdog.replace_local_dot_directory(line.replace("Icon=", ""))
            open(backup_watchdog.replace_local_dot_directory("./BackupTool.desktop"), "w").writelines(lines)
            subprocess.run(["chmod", "+x", backup_watchdog.replace_local_dot_directory("./BackupTool.desktop")])
            try: os.remove(str(Path.home()) + "/.local/share/applications/BackupTool.desktop")
            except: pass
            shutil.move(backup_watchdog.replace_local_dot_directory("./BackupTool.desktop"), str(Path.home()) + "/.local/share/applications")
        if sys.platform == "win32":
            winshell.CreateShortcut(Path=backup_watchdog.replace_local_dot_directory("./Save Game Backup Tool.lnk"),
                                    Target=backup_watchdog.replace_local_dot_directory("./BackupTool.exe"),
                                    Icon=(backup_watchdog.replace_local_dot_directory("./BackupTool.exe"), 0))
            try: os.remove(backup_watchdog.replace_local_dot_directory(os.getenv("APPDATA")) + "/Microsoft/Windows/Start Menu/Programs/Save Game Backup Tool.lnk")
            except: pass
            shutil.move(backup_watchdog.replace_local_dot_directory("./Save Game Backup Tool.lnk"),
                        backup_watchdog.replace_local_dot_directory(os.getenv("APPDATA")) + "/Microsoft/Windows/Start Menu/Programs")

        self.backup_configs = []
        self.backup_threads = []
        self.configs_used = []

        data = json.load(open(backup_watchdog.replace_local_dot_directory("./MasterConfig.json"), "r"))

        config_path = None
        skip_choice = False
        no_gui = False
        for arg in sys.argv:
            if arg.lower() == "--no-gui": no_gui = True
            elif arg.lower() == "--skip-choice": skip_choice = True
        if skip_choice:
            for config in data["configurations"]:
                if config["name"] == data["default"]: config_path = config["file"]
        index = 0
        while index < len(sys.argv) and not skip_choice:
            if sys.argv[index].lower() == "--config" and index < len(sys.argv) - 1:
                config_path = sys.argv[index + 1].replace(".json", "") + ".json"
                break
            index += 1

        if no_gui:
            try: interval = data["interval"]
            except: interval = 0
            self.stop_queue = []
            self.stop_backup_tool = False
            if config_path is not None:
                self.backup_configs.append(BackupConfig(data["default"], config_path, interval))
                self.backup_threads.append(threading.Thread(target=self.backup_configs[0].watchdog, args=(self.stop_queue,)))
                self.backup_threads[0].start()
            else: print("Enter in \"help\" or \"?\" for assistance.")
            while config_path is None:
                print(backup_watchdog.prompt, end="")
                choice = input()
                if choice == "start":
                    config = self.add_or_remove_config(config_path, data["configurations"])
                    if config not in self.configs_used:
                        self.configs_used.append(config)
                        self.backup_configs.append(BackupConfig(config["name"], config["file"], interval, True))
                        self.backup_threads.append(threading.Thread(target=self.backup_configs[len(self.backup_configs) - 1].watchdog,
                                                                    args=(self.stop_queue, None, self, config)))
                        self.backup_threads[len(self.backup_threads) - 1].start()
                    else: print("That configuration is already in use.")
                elif choice == "stop":
                    config = self.add_or_remove_config(config_path, data["configurations"])
                    self.remove_config(config)
                elif choice == "end" or choice == "exit" or choice == "quit":
                    for backup_config in self.backup_configs:
                        self.stop_queue.append(backup_config.name)
                        while not backup_config.stop: pass
                    self.stop_queue = []
                    self.backup_configs = []
                    self.configs_used = []
                    self.stop_backup_tool = True
                elif choice == "help" or choice == "?": print("Enter in \"start\" to initialize a backup configuration.\n" +
                                                              "Enter in \"stop\" to suspend a backup configuration.\n" +
                                                              "Enter in \"end\", \"exit\", or \"quit\" to shut down this tool.")
                elif choice != "": print("Invalid command")
                if self.stop_backup_tool: break
        else:
            app = wx.App()
            frame = BackupGUI(None, wx.ID_ANY, "")
            frame.Show()
            app.MainLoop()

    def remove_config(self, config, wait=True):
        if config in self.configs_used:
            self.stop_queue.append(self.backup_configs[self.configs_used.index(config)].name)
            while wait and not self.backup_configs[self.configs_used.index(config)].stop: pass
            self.stop_queue.remove(self.backup_configs[self.configs_used.index(config)].name)
            self.backup_configs.remove(self.backup_configs[self.configs_used.index(config)])
            self.configs_used.remove(config)
        else: print("That configuration was not in use.")

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
backup_watchdog = BackupWatchdog()
backup_tool = BackupTool()
backup_tool.main()
