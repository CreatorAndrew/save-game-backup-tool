from __future__ import with_statement
from __future__ import absolute_import
from __future__ import print_function
import os
import sys
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
    def replace_local_dot_directory(self, path): return (path.replace(u"./", os.path.dirname(os.path.abspath(__file__)).replace(u"\\", u"/") + u"/")
                                                             .replace(u"/Save Game Backup Tool.app/Contents/MacOS", u""))

    def add_to_text_ctrl(self, text, text_ctrl=None):
        if text_ctrl is not None: wx.CallAfter(text_ctrl.AppendText, text + u"\n")
        return text

    def watchdog(self, config_file, text_ctrl=None, button_config=None, button_index=None, use_prompt=False, enabled=True):
        if not enabled: return

        config_file = self.replace_local_dot_directory(u"./" + config_file)
        data = json.load(open(config_file, u"r"))

        save_paths = []
        for save_path in data[u"searchableSavePaths"]: save_paths.append(save_path)
        if data[u"backupPath"][u"isAbsolute"]: home = u""
        else: home = unicode(Path.home()) + u"/"
        backup_folder = self.replace_local_dot_directory(home + data[u"backupPath"][u"path"])

        save_path = None
        for path in save_paths:
            if path[u"isAbsolute"]: home = u""
            else: home = unicode(Path.home()) + u"/"
            temp_save_path = self.replace_local_dot_directory(home + path[u"path"])
            if os.path.exists(temp_save_path):
                save_path = temp_save_path
                break
        if save_path is None:
            if text_ctrl is None and use_prompt: print(u"")
            print(self.add_to_text_ctrl(u"No save file found", text_ctrl))
            if text_ctrl is None and use_prompt: print(self.prompt, end=u"", flush=True)
            if button_config is not None:
                if text_ctrl is None: button_config.remove_config(button_index, False)
                else: wx.CallAfter(button_config.remove_config, button_index)
            return True
        save_folder = save_path[:save_path.rindex(u"/") + 1]

        if not os.path.exists(backup_folder): os.makedirs(backup_folder)

        # Sometimes on Linux, when Steam launches a game like Bully: Scholarship Edition, the path to the compatdata folder becomes briefly inaccessible.
        if os.path.exists(save_folder):
            if int(self.get_modified_date(save_path)) > data[u"lastBackupTime"]:
                data[u"lastBackupTime"] = int(self.get_modified_date(save_path))

                backup = data[u"backupFileNamePrefix"] + u"+" + unicode(data[u"lastBackupTime"]) + u".zip"
                if not backup_folder.endswith(u"/"): backup_folder = backup_folder + u"/"
                
                if text_ctrl is None and use_prompt: print(u"")
                if os.path.exists(backup_folder + backup):
                    if backup_folder.endswith(u"/"): backup_folder = backup_folder[:len(backup_folder) - 1]
                    print(self.add_to_text_ctrl(backup + u" already exists in " + backup_folder.replace(u"/", separator) + u".\nBackup cancelled", text_ctrl))
                else:
                    # Create the backup archive file
                    with ZipFile(backup_folder + backup, u"w") as backup_archive:
                        print(self.add_to_text_ctrl(u"Creating backup archive: " + backup, text_ctrl))
                        for folder, subFolders, files in os.walk(save_folder):
                            for file in files:
                                print(self.add_to_text_ctrl(u"Added " + file, text_ctrl))
                                path = os.path.join(folder, file)
                                backup_archive.write(path, os.path.basename(path), compress_type=zipfile.ZIP_DEFLATED)
                        if os.path.exists(backup_folder + backup): print(self.add_to_text_ctrl(u"Backup successful", text_ctrl))
                if text_ctrl is None and use_prompt: print(self.prompt, end=u"", flush=True)
                # Update the JSON file
                content = json.dumps(data, indent=4, ensure_ascii=False)
                if isinstance(content, str): content = content.decode(u"utf-8")
                open(config_file, u"w", encoding=u"utf-8").write(content)

temp_history = TempHistory()
print = temp_history.print
if sys.platform == u"win32": separator = u"\\"
else: separator = u"/"
