from __future__ import absolute_import
from __future__ import print_function
import sys

if sys.platform == u"win32":
    try: import colorama
    except ImportError:
        import ctypes
        kernel32 = ctypes.windll.kernel32
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
    else: colorama.init()
else: import readline

class TempHistory(object):
    def __init__(self):
        self.line = u"\n"
        self.builtin_print = print
        self.builtin_input = raw_input

    def _record(self, text):
        if text == u"": return
        lines = text.split(u"\n")
        if text[-1] == u"\n": last_line = lines[-2] + u"\n"
        else: last_line = lines[-1]
        last_line = last_line.split(u"\r")[-1]
        if self.line[-1] == u"\n": self.line = last_line
        else: self.line += last_line

    def _undo_newline(self):
        line_length = len(self.line)
        for i, char in enumerate(self.line[1:]):
            if char == u"\b" and self.line[i-1] != u"\b": line_length -= 2
        self.print(u"\x1b[{}C\x1b[1A".format(line_length), end=u"", flush=True, record=False)

    def print(self, *args, **_3to2kwargs):
        if u"record" in _3to2kwargs: record = _3to2kwargs[u"record"]; del _3to2kwargs[u"record"]
        else: record = True
        if u"flush" in _3to2kwargs: flush = _3to2kwargs[u"flush"]; del _3to2kwargs[u"flush"]
        else: flush = False
        if u"file" in _3to2kwargs: file = _3to2kwargs[u"file"]; del _3to2kwargs[u"file"]
        else: file = sys.stdout
        if u"end" in _3to2kwargs: end = _3to2kwargs[u"end"]; del _3to2kwargs[u"end"]
        else: end = u"\n"
        if u"sep" in _3to2kwargs: sep = _3to2kwargs[u"sep"]; del _3to2kwargs[u"sep"]
        else: sep = u" "
        self.builtin_print(*args, sep=sep, end=end, file=file)
        if flush: sys.stdout.flush()
        if record:
            text = sep.join([unicode(arg) for arg in args]) + end
            self._record(text)

    def input(self, prompt=u"", newline=True, record=True):
        if prompt == u"": prompt = u" \b"
        response = self.builtin_input(prompt)
        if record:
            self._record(prompt)
            self._record(response)
        if not newline: self._undo_newline()
        return response
