import os
import time
import json
import wx
import zipfile
from zipfile import ZipFile
from pathlib import Path
from TempHistory import TempHistory

class BackupWatchdog:
    prompt = "> "

    def get_modified_date(self, path): return time.strftime("%Y%m%d%H%M%S", time.strptime(time.ctime(os.path.getmtime(path))))

    # This method makes it so that this program treats the filesystem as relative to its own path.
    def replace_local_dot_directory(self, path):
        return (path.replace("./", os.path.dirname(os.path.abspath(__file__)).replace("\\", "/") + "/")
                    .replace("/_internal", "")
                    .replace("/Save Game Backup Tool.app/Contents/Frameworks", ""))

    def add_text_to_text_area(self, text, text_area=None):
        if text_area is not None: wx.CallAfter(text_area.AppendText, text + "\n")
        return text

    def watchdog(self, config_file, text_area=None, button_config=None, button_index=None, use_prompt=False, enabled=True):
        if not enabled: return

        save_paths = []

        config_file = self.replace_local_dot_directory("./" + config_file)

        with open(config_file, "r") as read_file:
            data = json.load(read_file)
            for save_path in data["searchableSavePaths"]: save_paths.append(save_path)
            if data["backupPath"]["isAbsolute"]: home = ""
            else: home = str(Path.home()) + "/"
            backup_folder = self.replace_local_dot_directory(home + data["backupPath"]["path"])
            backup_file_name_prefix = data["backupFileNamePrefix"]
            last_backup_time = data["lastBackupTime"]

        save_path = None
        for path in save_paths:
            if path["isAbsolute"]: home = ""
            else: home = str(Path.home()) + "/"
            temp_save_path = self.replace_local_dot_directory(home + path["path"])
            if os.path.exists(temp_save_path):
                save_path = temp_save_path
                break
        if save_path is None:
            if text_area is None and use_prompt: print("")
            print(self.add_text_to_text_area("No save file found", text_area))
            if text_area is None and use_prompt: print(self.prompt, end="", flush=True)
            if button_config is not None:
                if text_area is None: button_config.remove_config(button_index, False)
                else: wx.CallAfter(button_config.remove_config, button_index, False)
            return True
        save_folder = save_path[:save_path.rindex("/") + 1]

        if not os.path.exists(backup_folder): os.makedirs(backup_folder)

        try:
            if int(self.get_modified_date(save_path)) > last_backup_time:
                last_backup_time = int(self.get_modified_date(save_path))

                backup = backup_file_name_prefix + "+" + str(last_backup_time) + ".zip"
                if not backup_folder.endswith("/"): backup_folder = backup_folder + "/"

                if text_area is None and use_prompt: print("")
                if os.path.exists(backup_folder + backup):
                    if backup_folder.endswith("/"): backup_folder = backup_folder[:len(backup_folder) - 1]
                    print(self.add_text_to_text_area(backup + " already exists in " + backup_folder + ".\nBackup cancelled", text_area))
                else:
                    # Create the backup archive file
                    with ZipFile(backup_folder + backup, "w") as backup_archive:
                        print(self.add_text_to_text_area("Creating backup archive: " + backup, text_area))
                        for folder, subFolders, files in os.walk(save_folder):
                            for file in files:
                                print(self.add_text_to_text_area("Added " + file, text_area))
                                path = os.path.join(folder, file)
                                backup_archive.write(path, os.path.basename(path), compress_type=zipfile.ZIP_DEFLATED)
                        if os.path.exists(backup_folder + backup): print(self.add_text_to_text_area("Backup successful", text_area))
                if text_area is None and use_prompt: print(self.prompt, end="", flush=True)
                # Update the JSON file
                data["lastBackupTime"] = last_backup_time
                with open(config_file, "w") as write_file: json.dump(data, write_file, indent=4)
        # Sometimes on Linux, when Steam launches a game like Bully: Scholarship Edition, the path to the compatdata folder becomes briefly inaccessible.
        except FileNotFoundError: pass

temp_history = TempHistory()
print = temp_history.print
