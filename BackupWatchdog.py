from __future__ import with_statement
from __future__ import absolute_import
from __future__ import print_function
import os
import time
import json
import wx
import zipfile
from zipfile import ZipFile
from pathlib2 import Path
from io import open
from TempHistory import TempHistory

class BackupWatchdog(object):
    prompt = u"> "

    def get_modified_date(self, path): return time.strftime(u"%Y%m%d%H%M%S", time.strptime(time.ctime(os.path.getmtime(path))))

    # This method makes it so that this program treats the filesystem as relative to its own path.
    def replace_local_dot_directory(self, path):
        return (path.replace(u"./", os.path.dirname(os.path.abspath(__file__)).replace(u"\\", u"/") + u"/")
                    .replace(u"/_internal", u"")
                    .replace(u"/BackupTool.app/Contents/Frameworks", u""))

    def add_text_to_text_area(self, text, text_area=None):
        if text_area is not None: wx.CallAfter(text_area.AppendText, text + u"\n")
        return text

    def watchdog(self, config_file, text_area=None, button_config=None, button_index=None, use_prompt=False, enabled=True):
        if not enabled: return

        save_paths = []

        config_file = self.replace_local_dot_directory(u"./" + config_file)

        with open(config_file, u"r") as read_file:
            data = json.load(read_file)
            for save_path in data[u"searchableSavePaths"]: save_paths.append(save_path)
            if data[u"backupPath"][u"isAbsolute"]: home = u""
            else: home = unicode(Path.home()) + u"/"
            backup_folder = self.replace_local_dot_directory(home + data[u"backupPath"][u"path"])
            backup_file_name_prefix = data[u"backupFileNamePrefix"]
            last_backup_time = data[u"lastBackupTime"]

        save_path = None
        for path in save_paths:
            if path[u"isAbsolute"]: home = u""
            else: home = unicode(Path.home()) + u"/"
            temp_save_path = self.replace_local_dot_directory(home + path[u"path"])
            if os.path.exists(temp_save_path):
                save_path = temp_save_path
                break
        if save_path is None:
            if text_area is None and use_prompt: print(u"")
            print(self.add_text_to_text_area(u"No save file found", text_area))
            if text_area is None and use_prompt: print(self.prompt, end=u"", flush=True)
            if button_config is not None:
                if text_area is None: button_config.remove_config(button_index, False)
                else: wx.CallAfter(button_config.remove_config, button_index, False)
            return True
        save_folder = save_path[:save_path.rindex(u"/") + 1]

        if not os.path.exists(backup_folder): os.makedirs(backup_folder)

        # Sometimes on Linux, when Steam launches a game like Bully: Scholarship Edition, the path to the compatdata folder becomes briefly inaccessible.
        if os.path.exists(save_folder):
            if int(self.get_modified_date(save_path)) > last_backup_time:
                last_backup_time = int(self.get_modified_date(save_path))

                backup = backup_file_name_prefix + u"+" + unicode(last_backup_time) + u".zip"
                if not backup_folder.endswith(u"/"): backup_folder = backup_folder + u"/"
                
                if text_area is None and use_prompt: print(u"")
                if os.path.exists(backup_folder + backup):
                    if backup_folder.endswith(u"/"): backup_folder = backup_folder[:len(backup_folder) - 2]
                    print(self.add_text_to_text_area(backup + u" already exists in " + backup_folder + u".\nBackup cancelled", text_area))
                else:
                    # Create the backup archive file
                    with ZipFile(backup_folder + backup, u"w") as backup_archive:
                        print(self.add_text_to_text_area(u"Creating backup archive: " + backup, text_area))
                        for folder, subFolders, files in os.walk(save_folder):
                            for file in files:
                                print(self.add_text_to_text_area(u"Added " + file, text_area))
                                path = os.path.join(folder, file)
                                backup_archive.write(path, os.path.basename(path), compress_type=zipfile.ZIP_DEFLATED)
                        if os.path.exists(backup_folder + backup): print(self.add_text_to_text_area(u"Backup successful", text_area))
                if text_area is None and use_prompt: print(self.prompt, end=u"", flush=True)
                # Update the JSON file
                data[u"lastBackupTime"] = last_backup_time
                with open(config_file, u"w", encoding="utf-8") as write_file:
                    content = json.dumps(data, indent=4, ensure_ascii=False)
                    if isinstance(content, str): content = content.decode("utf-8")
                    write_file.write(content)

temp_history = TempHistory()
print = temp_history.print
