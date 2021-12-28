import sys
import time
import curses as cs
from modules import yle_module
from modules import crypto_module
from modules import toolbar_module

# todo:
# resize article pad
# arguments
# some keys must be disabled during NO ROOM


H_PAD = 1

LOAD_CRYPTO = True
CRYPTOS = ["BTC", "ETH", "AAVE", "MATIC", "LINK", "DOGE", "MANA"]
# CRYPTOS = ["ETH"]

MIN_Y = 4
if LOAD_CRYPTO is True:
    MIN_Y += len(CRYPTOS)
MIN_X = 20


def debugg(joku):
    cs.endwin()
    print(joku)
    sys.exit(0)


def terminate_program(msg=0):
    sys.exit(msg)


def touch_and_refresh(wins):
    for win in wins:
        wins[win].touchwin()
        wins[win].refresh()


def initialize_screen(scr):
    cs.curs_set(0)
    cs.use_default_colors()
    cs.init_pair(1, cs.COLOR_CYAN, -1)
    cs.init_pair(2, cs.COLOR_RED, -1)

    bool_ = is_screensize_sufficient(scr)
    if bool_ is False:
        msg = "Terminal window is too small, minimum height is " + str(MIN_Y) \
                + " and width " + str(MIN_X)
        terminate_program(msg)

    max_y, max_x = scr.getmaxyx()
    return max_y, max_x


def is_screensize_sufficient(stdscr):
    is_sufficient = True
    max_y, max_x = stdscr.getmaxyx()

    if max_x < MIN_X:
        is_sufficient = False
    if max_y < MIN_Y:
        is_sufficient = False
    return is_sufficient


def resize_windows(stdscr, win):
    scr_is_good_size = is_screensize_sufficient(stdscr)
    if scr_is_good_size is False:
        for w in win:
            win[w].win.clear()
        touch_and_refresh(win)
        return False

    win["toolbar"].win.addstr(0, 0, "Resizing window...")
    win["toolbar"].refresh()

    current_y = 0
    new_y, new_x = stdscr.getmaxyx()
    win["toolbar"].resize_window(new_x)
    if LOAD_CRYPTO is True:
        win["crypto"].resize_window(new_y, new_x)
        crypto_y, crypto_x = win["crypto"].win.getmaxyx()
        current_y += crypto_y

    win["yle"].resize_window(new_y - current_y - 3, new_x - (H_PAD * 2))
    win["yle"].win.mvwin(current_y, H_PAD)

    win["toolbar"].win.clear()
    win["toolbar"].refresh()
    touch_and_refresh(win)
    return True


def main(stdscr):
    max_y, max_x = initialize_screen(stdscr)

    current_y = 0
    win = {}

    toolbar_win = cs.newwin(1, max_x, max_y - 1, H_PAD)
    toolbar_m = toolbar_module.toolbar_module(toolbar_win)
    win["toolbar"] = toolbar_m

    win["toolbar"].win.addstr(0, 0, "Initalizing...")
    win["toolbar"].refresh()

    if LOAD_CRYPTO is True:
        crypto_y = len(CRYPTOS) + 1
        crypto_x = max_x - (H_PAD * 2)
        crypto_win = cs.newwin(crypto_y, crypto_x, current_y, H_PAD)
        crypto_m = crypto_module.crypto_module(crypto_win, CRYPTOS)
        crypto_y = crypto_m.adjust_win_height()

        current_y += crypto_y
        win["crypto"] = crypto_m

    yle_y = max_y - current_y - 2
    yle_x = max_x - (H_PAD * 2)
    yle_win = cs.newwin(yle_y, yle_x, current_y, H_PAD)
    yle_m = yle_module.yle_module(stdscr, yle_win, H_PAD,
                                  win["toolbar"].win)

    current_y += yle_y
    win["yle"] = yle_m

    while True:
        if LOAD_CRYPTO is True:
            win["crypto"].fetch_crypto()
        win["yle"].fetch_json()
        win["yle"].parse_json_data()

        if LOAD_CRYPTO is True:
            win["crypto"].print_crypto()
            win["crypto"].refresh()
        win["yle"].print_data()
        win["yle"].refresh()

        win["toolbar"].win.erase()
        timer_start = time.perf_counter()
        timer_end = timer_start + 1800
        cs.halfdelay(1)
        while time.perf_counter() < timer_end:
            try:
                key = win["toolbar"].win.getch()
            except Exception:
                key = False

            if key == ord('u'):
                break
            elif key == ord('n'):
                win["yle"].change_page(1)
                win["yle"].refresh()
            elif key == ord('b'):
                win["yle"].change_page(-1)
                win["yle"].refresh()
            elif key == ord('t'):
                win["yle"].print_content_pad(0)
                touch_and_refresh(win)
            elif key == ord('q'):
                terminate_program()
            elif key == cs.KEY_RESIZE:
                resize_windows(stdscr, win)
            elif key == ord('r'):
                prompt = "Read article (index): "
                input_str = win["toolbar"].take_input(prompt)

                pad_success = win["yle"].display_content_pad(input_str)
                if pad_success is True:
                    touch_and_refresh(win)
                else:
                    msg = "Invalid article index!"
                    win["toolbar"].win.addstr(msg)
                    win["toolbar"].refresh()

        win["toolbar"].win.erase()
        win["toolbar"].win.addstr(0, 0, "Refreshing...")
        win["toolbar"].refresh()


cs.wrapper(main)
