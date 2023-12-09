from __future__ import with_statement
from __future__ import absolute_import
from __future__ import print_function
import os
import sys
import shutil
import threading
import json
import wx
from pathlib2 import Path
from io import open
from TempHistory import TempHistory
from BackupWatchdog import BackupWatchdog
from BackupConfig import BackupConfig
from BackupGUI import BackupGUI

if sys.platform == u"win32": import winshell

class BackupTool(wx.App):
    def main(self):
        if sys.platform == u"darwin": os.system(u"clear")
        if sys.platform == u"linux" and os.path.exists(backup_watchdog.replace_local_dot_directory(u"./.BackupTool.desktop")):
            shutil.copy(backup_watchdog.replace_local_dot_directory(u"./.BackupTool.desktop"),
                        backup_watchdog.replace_local_dot_directory(u"./BackupTool.desktop"))
            with open(backup_watchdog.replace_local_dot_directory(u"./BackupTool.desktop"), u"r") as read_file: lines = read_file.readlines()
            for line in lines:
                lines[lines.index(line)] = line = backup_watchdog.replace_local_dot_directory(line)
                if u"Exec=" in line: lines[lines.index(line)] = u"Exec=\"" + line.replace(u"Exec=", u"").replace(u"\n", u"\"\n")
            with open(backup_watchdog.replace_local_dot_directory(u"./BackupTool.desktop"), u"w") as write_file: write_file.writelines(lines)
            os.system(u"chmod +x ./BackupTool.desktop")
            try: os.remove(unicode(Path.home()) + u"/.local/share/applications/BackupTool.desktop")
            except: pass
            shutil.move(backup_watchdog.replace_local_dot_directory(u"./BackupTool.desktop"), unicode(Path.home()) + u"/.local/share/applications")
        if sys.platform == u"win32":
            winshell.CreateShortcut(Path=backup_watchdog.replace_local_dot_directory(u"./Save Game Backup Tool.lnk"),
                                    Target=backup_watchdog.replace_local_dot_directory(u"./BackupTool.exe"),
                                    Icon=(backup_watchdog.replace_local_dot_directory(u"./BackupTool.exe"), 0))
            try: os.remove(backup_watchdog.replace_local_dot_directory(os.getenv(u"APPDATA")) + u"/Microsoft/Windows/Start Menu/Programs/Save Game Backup Tool.lnk")
            except:
                try: os.remove(backup_watchdog.replace_local_dot_directory(unicode(Path.home())) + u"/Start Menu/Programs/Save Game Backup Tool.lnk")
                except: pass
            try: shutil.move(backup_watchdog.replace_local_dot_directory(u"./Save Game Backup Tool.lnk"),
                             backup_watchdog.replace_local_dot_directory(os.getenv(u"APPDATA")) + u"/Microsoft/Windows/Start Menu/Programs")
            except: shutil.move(backup_watchdog.replace_local_dot_directory(u"./Save Game Backup Tool.lnk"),
                                backup_watchdog.replace_local_dot_directory(unicode(Path.home())) + u"/Start Menu/Programs")

        self.backup_configs = []
        self.backup_threads = []
        self.configs_used = []

        with open(backup_watchdog.replace_local_dot_directory(u"./MasterConfig.json"), u"r") as read_file:
            data = json.load(read_file)
            configs = data[u"configurations"]
            default_config_name = data[u"default"]

        config_path = None
        skip_choice = False
        no_gui = False
        for arg in sys.argv:
            if arg.lower() == u"--no-gui": no_gui = True
            elif arg.lower() == u"--skip-choice": skip_choice = True
        if skip_choice:
            for config in configs:
                if config[u"name"] == default_config_name: config_path = config[u"file"]
        index = 0
        while index < len(sys.argv) and not skip_choice:
            if sys.argv[index].lower() == u"--config" and index < len(sys.argv) - 1:
                config_path = sys.argv[index + 1].replace(u".json", u"") + u".json"
                break
            index += 1

        if no_gui:
            self.stop_queue = []
            self.stop_backup_tool = False
            if config_path is not None:
                self.backup_configs.append(BackupConfig(name=u"Single Config", path=config_path))
                self.backup_threads.append(threading.Thread(target=self.backup_configs[0].watchdog, args=(self.stop_queue,)))
                self.backup_threads[0].start()
            else: print(u"Enter in \"help\" or \"?\" for assistance.")
            while config_path is None:
                print(backup_watchdog.prompt, end=u"")
                choice = input()
                if choice == u"start":
                    config = self.add_or_remove_config(config_path, configs)
                    if config not in self.configs_used:
                        self.configs_used.append(config)
                        self.backup_configs.append(BackupConfig(name=config[u"name"], path=config[u"file"], use_prompt=True))
                        self.backup_threads.append(threading.Thread(target=self.backup_configs[len(self.backup_configs) - 1].watchdog,
                                                                    args=(self.stop_queue, None, self, config)))
                        self.backup_threads[len(self.backup_threads) - 1].start()
                    else: print(u"That configuration is already in use.")
                elif choice == u"stop":
                    config = self.add_or_remove_config(config_path, configs)
                    self.remove_config(config)
                elif choice == u"exit" or choice == u"quit" or choice == u"end":
                    for backup_config in self.backup_configs: 
                        self.stop_queue.append(backup_config.name)
                        while not backup_config.stop: pass
                    self.stop_queue = []
                    self.backup_configs = []
                    self.configs_used = []
                    self.stop_backup_tool = True
                elif choice == u"help" or choice == u"?": print(u"Enter in \"start\" to initialize a backup configuration.\n"
                                                              + u"Enter in \"stop\" to suspend a backup configuration.\n"
                                                              + u"Enter in \"exit\", \"quit\", or \"end\" to shut down this tool.")
                elif choice != u"": print(u"Invalid command")
                if self.stop_backup_tool: break
        else:
            app = wx.App()
            frame = BackupGUI(None, wx.ID_ANY, u"")
            frame.Show()
            app.MainLoop()

    def remove_config(self, config, wait=True):
        if config in self.configs_used:
            self.stop_queue.append(self.backup_configs[self.configs_used.index(config)].name)
            while wait and not self.backup_configs[self.configs_used.index(config)].stop: pass
            self.stop_queue.remove(self.backup_configs[self.configs_used.index(config)].name)
            self.backup_configs.remove(self.backup_configs[self.configs_used.index(config)])
            self.configs_used.remove(config)
        else: print(u"That configuration was not in use.")

    def add_or_remove_config(self, config_path, configs):
        if config_path is None:
            print(u"Select one of the following configurations:")
            index = 0
            for config in configs:
                print(u"    " + unicode(index) + u": " + config[u"name"])
                index += 1
            choice = None
            while choice is None: 
                try:
                    print(u"Enter in an option number here: ", end=u"")
                    choice = int(input())
                    if choice >= len(configs) or choice < 0:
                        print(u"Not a valid option number. Try again.")
                        choice = None
                except ValueError:
                    print(u"Invalid input value. Try again with a numeric value.")
                    choice = None
            config = configs[choice]
        return config

temp_history = TempHistory()
print = temp_history.print
input = temp_history.input
backup_watchdog = BackupWatchdog()
backup_tool = BackupTool()
backup_tool.main()
