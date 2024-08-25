from __future__ import absolute_import
from __future__ import print_function
from sys import platform, stdout

if platform == "win32":
    try:
        import colorama
    except ImportError:
        import ctypes

        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
    else:
        colorama.init()
else:
    import readline


class TempHistory:
    def __init__(self):
        self.line = "\n"
        self.builtin_print = print
        try:
            self.builtin_input = raw_input
        except:
            self.builtin_input = input

    def _record(self, text):
        if text == "":
            return
        lines = text.split("\n")
        if text[-1] == "\n":
            last_line = lines[-2] + "\n"
        else:
            last_line = lines[-1]
        last_line = last_line.split("\r")[-1]
        if self.line[-1] == "\n":
            self.line = last_line
        else:
            self.line += last_line

    def _undo_newline(self):
        line_length = len(self.line)
        for i, char in enumerate(self.line[1:]):
            if char == "\b" and self.line[i - 1] != "\b":
                line_length -= 2
        self.print(
            "\x1b[{}C\x1b[1A".format(line_length), end="", flush=True, record=False
        )

    def print(self, *args, **kwargs):
        if "record" in kwargs:
            record = kwargs["record"]
            del kwargs["record"]
        else:
            record = True
        if "flush" in kwargs:
            flush = kwargs["flush"]
            del kwargs["flush"]
        else:
            flush = False
        if "file" in kwargs:
            file = kwargs["file"]
            del kwargs["file"]
        else:
            file = stdout
        if "end" in kwargs:
            end = kwargs["end"]
            del kwargs["end"]
        else:
            end = "\n"
        if "sep" in kwargs:
            sep = kwargs["sep"]
            del kwargs["sep"]
        else:
            sep = " "
        self.builtin_print(*args, sep=sep, end=end, file=file)
        if flush:
            stdout.flush()
        if record:
            text = sep.join([str(arg) for arg in args]) + end
            self._record(text)

    def input(self, prompt="", newline=True, record=True):
        if prompt == "":
            prompt = " \b"
        response = self.builtin_input(prompt)
        if record:
            self._record(prompt)
            self._record(response)
        if not newline:
            self._undo_newline()
        return response
