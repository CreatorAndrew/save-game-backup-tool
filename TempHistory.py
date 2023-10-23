# For the sys.stdout file-like object
import sys
import platform

if platform.system() == 'Windows':
    try:
        import colorama
    except ImportError:
        import ctypes
        kernel32 = ctypes.windll.kernel32
        # Enable ANSI support on Windows 10 v1511
        kernel32.SetConsoleMode(kernel32.GetStdHandle(-11), 7)
    else:
        colorama.init()
else:
    # Fix Linux arrow key support in Python scripts
    import readline


class TempHistory:
    """Record one line from the terminal.

    It is necessary to keep track of the last line on the terminal so we
    can move the text cursor rightward and upward back into the position
    before the newline from the `input` function was echoed.

    Note: I use the term 'echo' to refer to when text is
    shown on the terminal but might not be written to `sys.stdout`.

    """

    def __init__(self):
        """Initialise `line` and save the `print` and `input` functions.

        `line` is initially set to '\n' so that the `record` method
        doesn't raise an error about the string index being out of range.

        """
        self.line = '\n'
        self.builtin_print = print
        self.builtin_input = input

    def _record(self, text):
        """Append to `line` or overwrite it if it has ended."""
        if text == '':
            # You can't record nothing
            return
        # Take into account `text` being multiple lines
        lines = text.split('\n')
        if text[-1] == '\n':
            last_line = lines[-2] + '\n'
            # If `text` ended with a newline, then `text.split('\n')[-1]`
            # would have merely returned the newline, and not the text
            # preceding it
        else:
            last_line = lines[-1]
        # Take into account return characters which overwrite the line
        last_line = last_line.split('\r')[-1]
        # `line` is considered ended if it ends with a newline character
        if self.line[-1] == '\n':
            self.line = last_line
        else:
            self.line += last_line

    def _undo_newline(self):
        """Move text cursor back to its position before echoing newline.

        ANSI escape sequence: `\x1b[{count}{command}`
        `\x1b` is the escape code, and commands `A`, `B`, `C` and `D` are
        for moving the text cursor up, down, forward and backward {count}
        times respectively.

        Thus, after having echoed a newline, the final statement tells
        the terminal to move the text cursor forward to be inline with
        the end of the previous line, and then move up into said line
        (making it the current line again).

        """
        line_length = len(self.line)
        # Take into account (multiple) backspaces which would
        # otherwise artificially increase `line_length`
        for i, char in enumerate(self.line[1:]):
            if char == '\b' and self.line[i-1] != '\b':
                line_length -= 2
        self.print('\x1b[{}C\x1b[1A'.format(line_length),
                   end='', flush=True, record=False)

    def print(self, *args, sep=' ', end='\n', file=sys.stdout, flush=False,
              record=True):
        """Print to `file` and record the printed text.

        Other than recording the printed text, it behaves exactly like
        the built-in `print` function.

        """
        self.builtin_print(*args, sep=sep, end=end, file=file, flush=flush)
        if record:
            text = sep.join([str(arg) for arg in args]) + end
            self._record(text)

    def input(self, prompt='', newline=True, record=True):
        """Return one line of user input and record the echoed text.

        Other than storing the echoed text and optionally stripping the
        echoed newline, it behaves exactly like the built-in `input`
        function.

        """
        if prompt == '':
            # Prevent arrow key overwriting previously printed text by
            # ensuring the built-in `input` function's `prompt` argument
            # isn't empty
            prompt = ' \b'
        response = self.builtin_input(prompt)
        if record:
            self._record(prompt)
            self._record(response)
        if not newline:
            self._undo_newline()
        return response