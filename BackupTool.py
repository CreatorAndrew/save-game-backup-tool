import sys
import threading
import json
import wx
import subprocess
from TempHistory import TempHistory
from BackupWatchdog import BackupWatchdog
from BackupConfig import BackupConfig
from BackupGUI import BackupGUI

class BackupTool(wx.App):
    def main(self):
        if sys.platform == "darwin": subprocess.run("clear")

        self.backup_configs = []
        self.backup_threads = []
        self.configs_used = []

        with open(backup_watchdog.replace_local_dot_directory("./MasterConfig.json"), "r") as read_file:
            data = json.load(read_file)
            configs = data["configurations"]
            default_config_name = data["default"]

        config_path = None
        skip_choice = False
        no_gui = False
        for arg in sys.argv:
            if arg.lower() == "--no-gui": no_gui = True
            elif arg.lower() == "--skip-choice": skip_choice = True
        if skip_choice:
            for config in configs:
                if config["name"] == default_config_name: config_path = config["file"]
        index = 0
        while index < len(sys.argv) and not skip_choice:
            if sys.argv[index].lower() == "--config" and index < len(sys.argv) - 1:
                config_path = sys.argv[index + 1]
                break
            index += 1

        if no_gui:
            self.stop_queue = []
            self.stop_backup_tool = False
            if config_path is not None:
                self.backup_configs.append(BackupConfig(name="Single Config", path=config_path))
                self.backup_threads.append(threading.Thread(target=self.backup_configs[0].watchdog, args=(self.stop_queue,)))
                self.backup_threads[0].start()
            else: print("Enter in \"help\" or \"?\" for assistance.")
            while config_path is None:
                print(backup_watchdog.prompt, end="")
                choice = input()
                if choice == "start":
                    config = self.add_or_remove_config(config_path, configs)
                    if config not in self.configs_used:
                        self.configs_used.append(config)
                        self.backup_configs.append(BackupConfig(name=config["name"], path=config["file"], use_prompt=True))
                        self.backup_threads.append(threading.Thread(target=self.backup_configs[len(self.backup_configs) - 1].watchdog, args=(self.stop_queue,)))
                        self.backup_threads[len(self.backup_threads) - 1].start()
                    else: print("That configuration is already in use.")
                elif choice == "stop":
                    config = self.add_or_remove_config(config_path, configs)
                    if config in self.configs_used:
                        self.stop_queue.append(self.backup_configs[self.configs_used.index(config)].name)
                        self.backup_threads[self.configs_used.index(config)].join()
                        while not self.backup_configs[self.configs_used.index(config)].stop: pass
                        self.stop_queue.remove(self.backup_configs[self.configs_used.index(config)].name)
                        self.backup_configs.remove(self.backup_configs[self.configs_used.index(config)])
                        self.configs_used.remove(config)
                    else: print("That configuration was not in use.")
                elif choice == "exit" or choice == "quit" or choice == "end": self.quit()
                elif choice == "help" or choice == "?": help()
                else: print("Invalid command")
                if self.stop_backup_tool: break
        else:
            app = wx.App()
            frame = BackupGUI(None, wx.ID_ANY, "")
            frame.Show()
            app.MainLoop()

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

    def quit(self):
        for backup_config in self.backup_configs: 
            self.stop_queue.append(backup_config.name)
            while not backup_config.stop: pass
        self.stop_queue = []
        self.backup_configs = []
        self.configs_used = []
        self.stop_backup_tool = True

def help():
    print("Enter in \"start\" to initialize a backup configuration.\n"
        + "Enter in \"stop\" to suspend a backup configuration.\n"
        + "Enter in \"exit\", \"quit\", or \"end\" to shut down this tool.")

temp_history = TempHistory()
print = temp_history.print
input = temp_history.input
backup_watchdog = BackupWatchdog()
backup_tool = BackupTool()
backup_tool.main()
