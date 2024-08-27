from os import listdir
from os.path import abspath, dirname
from sys import executable, platform, version_info
from wx import CallAfter

PROMPT = "> "


def add_to_text_ctrl(text, text_ctrl):
    if text_ctrl is not None:
        CallAfter(text_ctrl.AppendText, text + "\n")
    return text


# This method makes it so that this program treats the filesystem as relative to its own path.
def apply_working_directory(path):
    temp_path = path.replace("\\", "/")
    working_directory = dirname(
        abspath(__file__) if platform == "darwin" else executable
    ).replace("\\", "/")
    if temp_path == ".":
        temp_path = working_directory
    elif temp_path == "..":
        temp_path = dirname(working_directory)
    elif temp_path.startswith("./"):
        temp_path = temp_path.replace("./", working_directory + "/", 1)
    elif temp_path.startswith("../"):
        temp_path = temp_path.replace("../", dirname(working_directory) + "/", 1)
    return temp_path.replace(
        "/Save Game Backup Tool.app/Contents/"
        + ("MacOS" if version_info[0] == 2 else "Frameworks"),
        "",
    )


def get_files_in_lower_case(path):
    files = []
    for file in listdir(path):
        files.append(file.lower())
    return files
