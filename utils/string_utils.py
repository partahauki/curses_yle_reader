import curses as cs
import re
import sys


def debugg(joku):
    cs.endwin()
    print(joku)
    sys.exit(0)


def fit_text_to_rows(param_text, max_x):
    text = param_text
    failsafe = 0
    current_row = 0
    padding = 0
    while failsafe < 100:
        current_row += 1
        last_i = current_row * max_x - 1
        try:
            text[last_i]
        except IndexError:
            return text
        first_i = last_i - max_x - 1

        if text[last_i] != ' ':
            padding += 1
            for i in range((last_i - 1), first_i, -1):
                if text[i] == ' ':
                    text = text[:i] + (padding * ' ') + text[i:]
                    current_row = 0
                    padding = 0
                    break
                padding += 1

                if i == first_i + 1:
                    return param_text
        failsafe += 1

    return param_text


def curses_print_markdown(win, text):
    i = 0
    continue_from = 0
    while i < len(text):
        if text[i:i+3] == "###":
            win.addstr(text[continue_from:i])
            i += 4
            occ = text.find('\n\n', i, len(text))
            win.addstr(text[i:occ], cs.A_BOLD | cs.color_pair(1))
            i = continue_from = occ
        if text[i:i+2] == "**":
            match = re.search(r"^\*\*.*?\*\*", text[i:], re.DOTALL)
            if match is not None:
                end = i + match.end()
                win.addstr(text[continue_from:i])
                win.addstr(text[i+2:end-2], cs.A_BOLD)
                i = continue_from = end

        i += 1

    win.addstr(text[continue_from:i-1])
