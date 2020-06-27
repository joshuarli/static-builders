#!/usr/bin/env python3

import signal
signal.signal(signal.SIGPIPE, signal.SIG_DFL)
signal.signal(signal.SIGINT, signal.SIG_DFL)

import sys
import difflib
from os import get_terminal_size, environ

# XXX: Since I'm using ydiff like `git diff | ydiff | less`,
# both stdin and stdout are redirected, so we'll get inappropriate ioctl for those devices.
# But we can use stderr (fd 2)!
terminal_width = int(environ.get("YDIFF_WIDTH") or get_terminal_size(2)[0])

COLOR_RESET = "\x1b[0m"
COLOR_REVERSE = "\x1b[7m"
COLOR_PLAIN = "\x1b[22m"
COLOR_RED = "\x1b[31m"
COLOR_GREEN = "\x1b[32m"
COLOR_YELLOW = "\x1b[33m"
COLOR_CYAN = "\x1b[36m"
COLOR_GRAY = "\x1b[37m"

hunk_meta_display = f"{COLOR_GRAY}{'┈' * terminal_width}{COLOR_RESET}"


def strsplit(text, width):
    """strsplit() splits a given string into two substrings, \x1b-aware.

    It returns 3-tuple: (first string, second string, number of visible chars
    in the first string).

    If some color was active at the splitting point, then the first string is
    appended with the resetting sequence, and the second string is prefixed
    with all active colors.
    """
    first = ""
    found_colors = ""
    chars_cnt = 0

    while len(text):
        append_len = 0

        # First of all, check if current string begins with any escape sequence.
        if text[0] == "\x1b":
            color_end = text.find("m")
            if color_end != -1:
                color = text[:color_end+1]
                if color == COLOR_RESET:
                    found_colors = ""
                else:
                    found_colors += color
                append_len = len(color)

        if append_len == 0:
            # Current string does not start with any escape sequence, so,
            # either add one more visible char to the "first" string, or
            # break if that string is already large enough.
            if chars_cnt >= width:
                break
            chars_cnt += 1
            append_len = 1

        first += text[:append_len]
        text = text[append_len:]

    second = text

    # If the first string has some active colors at the splitting point,
    # reset it and append the same colors to the second string.
    if found_colors:
        return first + COLOR_RESET, found_colors + second, chars_cnt

    return first, second, chars_cnt


class Hunk(object):
    def __init__(self, hunk_headers, old_addr, new_addr):
        self._hunk_headers = hunk_headers
        self._old_addr = old_addr  # tuple (start, offset)
        self._new_addr = new_addr  # tuple (start, offset)
        self._hunk_list = []  # list of tuple (attr, line)

    def append(self, hunk_line):
        """hunk_line is a 2-element tuple: (attr, text), where attr is:
                '-': old, '+': new, ' ': common
        """
        self._hunk_list.append(hunk_line)

    def mdiff(self):
        """The difflib._mdiff() function returns an interator which returns a
        tuple: (from line tuple, to line tuple, boolean flag)

        from/to line tuple -- (line num, line text)
            line num -- integer or None (to indicate a context separation)
            line text -- original line text with following markers inserted:
                '\0+' -- marks start of added text
                '\0-' -- marks start of deleted text
                '\0^' -- marks start of changed text
                '\1' -- marks end of added/deleted/changed text

        boolean flag -- None indicates context separation, True indicates
            either "from" or "to" line contains a change, otherwise False.
        """
        return difflib._mdiff(self._get_old_text(), self._get_new_text())

    def _get_old_text(self):
        return [line for attr, line in self._hunk_list if attr != "+"]

    def _get_new_text(self):
        return [line for attr, line in self._hunk_list if attr != "-"]

    def is_completed(self):
        old_completed = self._old_addr[1] == len(self._get_old_text())
        if not old_completed:
            return False
        # new_completed
        return self._new_addr[1] == len(self._get_new_text())


class UnifiedDiff(object):
    def __init__(self, headers=None, old_path=None, new_path=None, hunks=None):
        self._headers = headers if headers else []
        self._old_path = old_path
        self._new_path = new_path
        self._hunks = hunks if hunks else []

    def is_old_path(self, line):
        return line.startswith("--- ")

    def is_new_path(self, line):
        return line.startswith("+++ ")

    def is_hunk_meta(self, line):
        return (
            line.startswith("@@ -")
            and line.find(" @@") >= 8
        )

    def parse_hunk_meta(self, hunk_meta):
        # @@ -3,7 +3,6 @@
        a = hunk_meta.split()[1].split(",")  # -3 7
        if len(a) > 1:
            old_addr = (int(a[0][1:]), int(a[1]))
        else:
            # @@ -1 +1,2 @@
            old_addr = (int(a[0][1:]), 1)

        b = hunk_meta.split()[2].split(",")  # +3 6
        if len(b) > 1:
            new_addr = (int(b[0][1:]), int(b[1]))
        else:
            # @@ -0,0 +1 @@
            new_addr = (int(b[0][1:]), 1)

        return old_addr, new_addr

    def parse_hunk_line(self, line):
        return line[0], line[1:]

    def is_old(self, line):
        return (
            line.startswith("-")
            and not self.is_old_path(line)
        )

    def is_new(self, line):
        return line.startswith("+") and not self.is_new_path(line)

    def is_common(self, line):
        return line.startswith(" ")

    def is_eof(self, line):
        # \ No newline at end of file
        # \ No newline at end of property
        return line.startswith(r"\ No newline at end of")

    def is_only_in_dir(self, line):
        return line.startswith("Only in ")

    def is_binary_differ(self, line):
        return line.startswith("Binary files") and line.endswith("differ")


class DiffParser(object):
    def __init__(self, stream):
        self._stream = stream

    def get_diff_generator(self):
        """parse all diff lines, construct a list of UnifiedDiff objects"""
        diff = UnifiedDiff()
        headers = []

        for line in self._stream:
            if diff.is_old_path(line):
                # This is a new diff when current hunk is not yet genreated or
                # is completed.  We yield previous diff if exists and construct
                # a new one for this case.  Otherwise it's acutally an 'old'
                # line starts with '--- '.
                if not diff._hunks or diff._hunks[-1].is_completed():
                    if diff._old_path and diff._new_path and diff._hunks:
                        yield diff
                    diff = UnifiedDiff(headers, line, None, None)
                    headers = []
                else:
                    diff._hunks[-1].append(diff.parse_hunk_line(line))

            elif diff.is_new_path(line) and diff._old_path:
                if not diff._new_path:
                    diff._new_path = line
                else:
                    diff._hunks[-1].append(diff.parse_hunk_line(line))

            elif diff.is_hunk_meta(line):
                hunk_meta = line
                old_addr, new_addr = diff.parse_hunk_meta(hunk_meta)
                hunk = Hunk(headers, old_addr, new_addr)
                headers = []
                diff._hunks.append(hunk)

            elif (
                diff._hunks
                and not headers
                and (diff.is_old(line) or diff.is_new(line) or diff.is_common(line))
            ):
                diff._hunks[-1].append(diff.parse_hunk_line(line))

            elif diff.is_eof(line):
                pass

            elif diff.is_only_in_dir(line) or diff.is_binary_differ(line):
                # 'Only in foo:' and 'Binary files ... differ' are considered
                # as separate diffs, so yield current diff, then this line
                #
                if diff._old_path and diff._new_path and diff._hunks:
                    # Current diff is comppletely constructed
                    yield diff
                headers.append(line)
                yield UnifiedDiff(headers, None, None, None)
                headers = []
                diff = UnifiedDiff()

            else:
                # All other non-recognized lines are considered as headers or
                # hunk headers respectively
                headers.append(line)

        # Validate and yield the last patch set if it is not yielded yet
        if diff._old_path:
            assert diff._new_path is not None
            if diff._hunks:
                assert len(diff._hunks[-1]._hunk_list) > 0
            yield diff

        if headers:
            # Tolerate dangling headers, just yield a UnifiedDiff object with
            # only header lines
            yield UnifiedDiff(headers, None, None, None)


class DiffMarker(object):
    def markup_side_by_side(self, diff):
        def _fit_with_marker_mix(text):
            """Wrap input text which contains mdiff tags, markup at the
            meantime
            """
            out = COLOR_PLAIN
            while text:
                if text.startswith("\x00-"):
                    out += f'{COLOR_REVERSE}{COLOR_RED}'
                    text = text[2:]
                elif text.startswith("\x00+"):
                    out += f'{COLOR_REVERSE}{COLOR_GREEN}'
                    text = text[2:]
                elif text.startswith("\x00^"):
                    out += f'{COLOR_REVERSE}{COLOR_YELLOW}'
                    text = text[2:]
                elif text.startswith("\x01"):
                    if len(text) > 1:
                        out += f'{COLOR_RESET}{COLOR_PLAIN}'
                    text = text[1:]
                else:
                    # FIXME: utf-8 wchar might break the rule here, e.g.
                    # u'\u554a' takes double width of a single letter, also
                    # this depends on your terminal font.  I guess audience of
                    # this tool never put that kind of symbol in their code :-)
                    out += text[0]
                    text = text[1:]

            return out + COLOR_RESET

        # Set up number width, note last hunk might be empty
        try:
            start, offset = diff._hunks[-1]._old_addr
            max1 = start + offset - 1
            start, offset = diff._hunks[-1]._new_addr
            max2 = start + offset - 1
        except IndexError:
            max1 = max2 = 0

        num_width = max(len(str(max1)), len(str(max2)))

        # Each line is like 'nnn TEXT nnn TEXT\n', so width is half of
        # [terminal size minus the line number columns and 3 separating spaces.
        width = (terminal_width - num_width * 2 - 3) // 2

        for line in diff._headers:
            yield f"{COLOR_CYAN}{line}{COLOR_RESET}"

        yield f"{COLOR_YELLOW}{diff._old_path}{COLOR_RESET}"
        yield f"{COLOR_YELLOW}{diff._new_path}{COLOR_RESET}"

        for hunk in diff._hunks:
            for hunk_header in hunk._hunk_headers:
                yield f"{COLOR_CYAN}{hunk_header}{COLOR_RESET}"

            yield hunk_meta_display

            for old, new, changed in hunk.mdiff():
                if old[0]:
                    left_num = str(hunk._old_addr[0] + int(old[0]) - 1)
                else:
                    left_num = " "

                if new[0]:
                    right_num = str(hunk._new_addr[0] + int(new[0]) - 1)
                else:
                    right_num = " "

                left = old[1].replace("\t", " " * 8).replace("\n", "").replace("\r", "")
                right = new[1].replace("\t", " " * 8).replace("\n", "").replace("\r", "")

                if changed:
                    if not old[0]:
                        left = ""
                        right = right.rstrip("\x01")
                        if right.startswith("\x00+"):
                            right = right[2:]
                        right = f"{COLOR_GREEN}{right}{COLOR_RESET}"
                    elif not new[0]:
                        left = left.rstrip("\x01")
                        if left.startswith("\x00-"):
                            left = left[2:]
                        left = f"{COLOR_RED}{left}{COLOR_RESET}"
                        right = ""
                    else:
                        left = _fit_with_marker_mix(left)
                        right = _fit_with_marker_mix(right)

                # Need to wrap long lines, so here we'll iterate,
                # shaving off `width` chars from both left and right
                # strings, until both are empty. Also, line number needs to
                # be printed only for the first part.
                lncur = left_num
                rncur = right_num
                while left or right:
                    # Split both left and right lines, preserving escaping
                    # sequences correctly.
                    lcur, left, llen = strsplit(left, width)
                    rcur, right, rlen = strsplit(right, width)

                    # Pad left line with spaces if needed
                    if llen < width:
                        lcur += " " * (width - llen)
                        # XXX: this doesn't work lol
                        # lcur = f"{lcur: <{width}}"

                    yield f"{COLOR_GRAY}{lncur:>{num_width}}{COLOR_RESET} {lcur} {COLOR_GRAY}{rncur:>{num_width}}{COLOR_RESET} {rcur}\n"

                    # Clean line numbers for further iterations
                    lncur = ""
                    rncur = ""


for diff in DiffParser(sys.stdin).get_diff_generator():
    for line in DiffMarker().markup_side_by_side(diff):
        sys.stdout.buffer.write(line.encode())
