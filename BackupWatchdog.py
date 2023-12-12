import os
import sys
import time
import json
import wx
import zipfile
from zipfile import ZipFile
from pathlib import Path
from TempHistory import TempHistory

class BackupWatchdog:
    prompt = "> "

    def get_modified_date(self, path): return int(time.strftime("%Y%m%d%H%M%S", time.strptime(time.ctime(os.path.getmtime(path)))))

    # This method makes it so that this program treats the filesystem as relative to its own path.
    def replace_local_dot_directory(self, path): return (path.replace("./", os.path.dirname(executable).replace("\\", "/") + "/")
                                                             .replace("/Save Game Backup Tool.app/Contents/Frameworks", ""))

    def add_to_text_ctrl(self, text, text_ctrl):
        if text_ctrl is not None: wx.CallAfter(text_ctrl.AppendText, text + "\n")
        return text

    def watchdog(self, config_file, text_ctrl, button_config, button_index, use_prompt, first_run):
        config_file = self.replace_local_dot_directory("./" + config_file)
        data = json.load(open(config_file, "r"))

        save_paths = []
        for save_path in data["searchableSavePaths"]: save_paths.append(save_path)
        if data["backupPath"]["isAbsolute"]: home = ""
        else: home = str(Path.home()) + "/"
        backup_folder = self.replace_local_dot_directory(home + data["backupPath"]["path"])

        save_path = None
        for path in save_paths:
            if path["isAbsolute"]: home = ""
            else: home = str(Path.home()) + "/"
            temp_save_path = self.replace_local_dot_directory(home + path["path"])
            if os.path.exists(temp_save_path):
                save_path = temp_save_path
                break
        if save_path is None:
            if first_run:
                if text_ctrl is None and use_prompt: print("")
                print(self.add_to_text_ctrl("No save file found", text_ctrl))
                if text_ctrl is None and use_prompt: print(self.prompt, end="", flush=True)
                if button_config is not None:
                    if text_ctrl is None: button_config.remove_config(button_index, False)
                    else: wx.CallAfter(button_config.remove_config, button_index)
                return True
            # Sometimes on Linux, when Steam launches a Windows game, the Proton prefix path becomes briefly inaccessible.
            return
        save_folder = save_path[:save_path.rindex("/") + 1]

        if not os.path.exists(backup_folder): os.makedirs(backup_folder)

        if self.get_modified_date(save_path) > data["lastBackupTime"]:
            data["lastBackupTime"] = self.get_modified_date(save_path)

            backup = data["backupFileNamePrefix"] + "+" + str(data["lastBackupTime"]) + ".zip"
            if not backup_folder.endswith("/"): backup_folder = backup_folder + "/"

            if text_ctrl is None and use_prompt: print("")
            if os.path.exists(backup_folder + backup):
                if backup_folder.endswith("/"): backup_folder = backup_folder[:len(backup_folder) - 1]
                print(self.add_to_text_ctrl(backup + " already exists in " + backup_folder.replace("/", separator) + ".\nBackup cancelled", text_ctrl))
            else:
                # Create the backup archive file
                with ZipFile(backup_folder + backup, "w") as backup_archive:
                    print(self.add_to_text_ctrl("Creating backup archive: " + backup, text_ctrl))
                    for folder, subFolders, files in os.walk(save_folder):
                        for file in files:
                            print(self.add_to_text_ctrl("Added " + file, text_ctrl))
                            path = os.path.join(folder, file)
                            backup_archive.write(path, os.path.basename(path), compress_type=zipfile.ZIP_DEFLATED)
                    if os.path.exists(backup_folder + backup): print(self.add_to_text_ctrl("Backup successful", text_ctrl))
            if text_ctrl is None and use_prompt: print(self.prompt, end="", flush=True)
            # Update the JSON file
            json.dump(data, open(config_file, "w"), indent=4)

temp_history = TempHistory()
print = temp_history.print
if sys.platform == "darwin": executable = os.path.abspath(__file__)
else: executable = sys.executable
if sys.platform == "win32": separator = "\\"
else: separator = "/"
