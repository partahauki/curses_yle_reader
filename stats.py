import sys
import time
import curses as cs
from modules import yle_module
from modules import crypto_module
from modules import toolbar_module

# todo:
# NO ROOM messages working
# refit screen errors


H_PAD = 1
LOAD_CRYPTO = True
LOAD_YLE = True
CRYPTOS = ["BTC", "ETH", "AAVE", "MATIC", "LINK", "DOGE", "MANA"]
# CRYPTOS = ["ETH"]


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
    cs.init_pair(2, cs.COLOR_GREEN, -1)

    max_y, max_x = scr.getmaxyx()
    min_y = len(CRYPTOS) + 4
    if max_x < 20:
        msg = "Terminal is too narrow, increase it's width to at least 20"
        terminate_program(msg)
    if max_y < min_y:
        msg = "Terminal is too short, increase it's height to at least "\
            + str(min_y)
        terminate_program(msg)
    return max_y, max_x


def main(stdscr):
    max_y, max_x = initialize_screen(stdscr)

    current_y = 0
    win = {"stdscr": stdscr}

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

    if LOAD_YLE is True:
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
        if LOAD_YLE is True:
            win["yle"].fetch_json()
            win["yle"].parse_json_data()

        if LOAD_CRYPTO is True:
            win["crypto"].print_crypto()
            win["crypto"].refresh()
        if LOAD_YLE is True:
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
                new_y, new_x = stdscr.getmaxyx()
                win["toolbar"].resize_window(new_x)
                win["crypto"].resize_window(new_y, new_x)
                crypto_y, crypto_x = win["crypto"].win.getmaxyx()
                win["yle"].win.mvwin(crypto_y, 0)
                win["yle"].resize_window(new_y - crypto_y - 3, new_x)
                touch_and_refresh(win)
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
