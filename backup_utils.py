from os.path import abspath, dirname
from sys import executable, platform
from wx import CallAfter

PROMPT = "> "


# This method makes it so that this program treats the filesystem as relative to its own path.
def apply_working_directory(path):
    temp_path = path.replace("\\", "/")
    working_directory = dirname(
        abspath(__file__) if platform == "darwin" else executable
    ).replace("\\", "/")
    if temp_path == ".":
        temp_path = working_directory
    elif temp_path == "..":
        temp_path = working_directory[: working_directory.rindex("/")]
    elif temp_path.startswith("./"):
        temp_path = temp_path.replace("./", working_directory + "/", 1)
    elif temp_path.startswith("../"):
        temp_path = temp_path.replace(
            "../", working_directory[: working_directory.rindex("/")] + "/", 1
        )
    return temp_path.replace("/Save Game Backup Tool.app/Contents/Frameworks", "")


def add_to_text_ctrl(text, text_ctrl):
    if text_ctrl is not None:
        CallAfter(text_ctrl.AppendText, text + "\n")
    return text
