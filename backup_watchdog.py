from __future__ import absolute_import
from __future__ import print_function
from __future__ import with_statement
from io import open
from json import load
from os import listdir, makedirs, walk
from os.path import basename, dirname, exists, getmtime, join
from sys import platform
from time import ctime, strftime, strptime
from zipfile import ZIP_DEFLATED, ZipFile
from backup_utils import add_to_text_ctrl, apply_working_directory, PROMPT
from temp_history import TempHistory

try:
    from pathlib import Path
except:
    from json import dumps
    from pathlib2 import Path
else:
    from json import dump


def get_modified_time(path):
    return int(strftime("%Y%m%d%H%M%S", strptime(ctime(getmtime(path)))))


def watchdog(config_file, text_ctrl, use_prompt, first_run):
    for file in listdir(apply_working_directory(".")):
        if (
            file.lower().endswith(".json")
            and file.lower() == config_file.lower().replace(".json", "") + ".json"
        ):
            config_file = apply_working_directory("./" + file)
            break
    data = load(open(config_file, "r"))
    backup_folder = apply_working_directory(
        (str(Path.home()) + "/" if data["backupPath"]["startsWithUserPath"] else "")
        + data["backupPath"]["path"]
    )
    save_path = None
    for searchable_save_path in data["searchableSavePaths"]:
        temp_save_path = apply_working_directory(
            (
                str(Path.home()) + "/"
                if searchable_save_path["startsWithUserPath"]
                else ""
            )
            + searchable_save_path["path"]
        )
        if exists(temp_save_path):
            save_path = temp_save_path
            break
    if save_path is None:
        if first_run:
            if text_ctrl is None and use_prompt:
                print()
            print(add_to_text_ctrl("No save file found", text_ctrl))
            if text_ctrl is None and use_prompt:
                print(PROMPT, end="", flush=True)
            return True
        # Sometimes on Linux, when Steam launches a Windows game, the Proton prefix path becomes briefly inaccessible.
        return
    makedirs(backup_folder, exist_ok=True)
    if get_modified_time(save_path) > data["lastBackupTime"]:
        data["lastBackupTime"] = get_modified_time(save_path)
        backup = (
            data["backupFileNamePrefix"] + "+" + str(data["lastBackupTime"]) + ".zip"
        )
        if text_ctrl is None and use_prompt:
            print()
        if exists(join(backup_folder, backup)):
            print(
                add_to_text_ctrl(
                    backup
                    + " already exists in "
                    + backup_folder[
                        : -1 if backup_folder.endswith("/") else None
                    ].replace("/", "\\" if platform == "win32" else "/")
                    + ".\nBackup cancelled",
                    text_ctrl,
                )
            )
        else:
            # Create the backup archive file
            with ZipFile(join(backup_folder, backup), "w") as backup_archive:
                print(add_to_text_ctrl("Creating backup archive: " + backup, text_ctrl))
                for directory, subdirectories, files in walk(dirname(save_path)):
                    for file in files:
                        print(add_to_text_ctrl("Added " + file, text_ctrl))
                        path = join(directory, file)
                        backup_archive.write(
                            path, basename(path), compress_type=ZIP_DEFLATED
                        )
                if exists(join(backup_folder, backup)):
                    print(add_to_text_ctrl("Backup successful", text_ctrl))
        if text_ctrl is None and use_prompt:
            print(PROMPT, end="", flush=True)
        # Update the JSON file
        try:
            dump(data, open(config_file, "w"), indent=4)
        except:
            open(config_file, "w", encoding="utf-8").write(
                dumps(data, indent=4, ensure_ascii=False).decode("utf-8")
            )


temp_history = TempHistory()
print = temp_history.print
