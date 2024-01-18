from __future__ import absolute_import
from __future__ import print_function
from __future__ import with_statement
from io import open
from pathlib2 import Path
from TempHistory import TempHistory
import json
import os
import sys
import time
import wx
import zipfile

class BackupWatchdog(object):
    prompt = u"> "

    def get_modified_time(self, path): return int(time.strftime(u"%Y%m%d%H%M%S", time.strptime(time.ctime(os.path.getmtime(path)))))

    # This method makes it so that this program treats the filesystem as relative to its own path.
    def replace_local_dot_directory(self, path):
        temp_path = path
        executable_path = os.path.dirname(os.path.abspath(__file__)).replace(u"\\", u"/")
        if temp_path == u".": temp_path = executable_path
        elif temp_path == u"..": temp_path = executable_path[:executable_path.rindex("/")]
        elif temp_path.startswith(u"./"): temp_path = temp_path.replace(u"./", executable_path + u"/", 1)
        elif temp_path.startswith(u"../"): temp_path = temp_path.replace(u"../", executable_path[:executable_path.rindex(u"/")] + u"/", 1)
        return temp_path.replace(u"/Save Game Backup Tool.app/Contents/MacOS", u"")

    def add_to_text_ctrl(self, text, text_ctrl):
        if text_ctrl is not None: wx.CallAfter(text_ctrl.AppendText, text + u"\n")
        return text

    def watchdog(self, config_file, text_ctrl, use_prompt, first_run):
        config_file = self.replace_local_dot_directory(u"./" + config_file)
        data = json.load(open(config_file, u"r"))
        backup_folder = self.replace_local_dot_directory((u"" if data[u"backupPath"][u"isAbsolute"] else unicode(Path.home()) + u"/") + data[u"backupPath"][u"path"])
        save_path = None
        for path in data[u"searchableSavePaths"]:
            temp_save_path = self.replace_local_dot_directory((u"" if path[u"isAbsolute"] else unicode(Path.home()) + u"/") + path[u"path"])
            if os.path.exists(temp_save_path):
                save_path = temp_save_path
                break
        if save_path is None:
            if first_run:
                if text_ctrl is None and use_prompt: print(u"")
                print(self.add_to_text_ctrl(u"No save file found", text_ctrl))
                if text_ctrl is None and use_prompt: print(self.prompt, end=u"", flush=True)
                return True
            # Sometimes on Linux, when Steam launches a Windows game, the Proton prefix path becomes briefly inaccessible.
            return
        save_folder = save_path[:save_path.rindex(u"/")]
        if not os.path.exists(backup_folder): os.makedirs(backup_folder)
        if self.get_modified_time(save_path) > data[u"lastBackupTime"]:
            data[u"lastBackupTime"] = self.get_modified_time(save_path)
            backup = data[u"backupFileNamePrefix"] + u"+" + unicode(data[u"lastBackupTime"]) + u".zip"
            if text_ctrl is None and use_prompt: print(u"")
            if os.path.exists(os.path.join(backup_folder, backup)):
                print(self.add_to_text_ctrl(backup +
                                            u" already exists in " +
                                            backup_folder[:-1 if backup_folder.endswith(u"/") else None].replace(u"/", u"\\" if sys.platform == u"win32" else u"/") +
                                            u".\nBackup cancelled",
                                            text_ctrl))
            else:
                # Create the backup archive file
                with zipfile.ZipFile(os.path.join(backup_folder, backup), u"w") as backup_archive:
                    print(self.add_to_text_ctrl(u"Creating backup archive: " + backup, text_ctrl))
                    for folder, sub_folders, files in os.walk(save_folder):
                        for file in files:
                            print(self.add_to_text_ctrl(u"Added " + file, text_ctrl))
                            path = os.path.join(folder, file)
                            backup_archive.write(path, os.path.basename(path), compress_type=zipfile.ZIP_DEFLATED)
                    if os.path.exists(os.path.join(backup_folder, backup)): print(self.add_to_text_ctrl(u"Backup successful", text_ctrl))
            if text_ctrl is None and use_prompt: print(self.prompt, end=u"", flush=True)
            # Update the JSON file
            content = json.dumps(data, indent=4, ensure_ascii=False)
            if isinstance(content, str): content = content.decode(u"utf-8")
            open(config_file, u"w", encoding=u"utf-8").write(content)

temp_history = TempHistory()
print = temp_history.print
separator = u"\\" if sys.platform == u"win32" else u"/"
