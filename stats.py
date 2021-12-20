import sys
import time
import curses as cs
import requests as req
from modules import yle_module

# todo:
# height checks for errors
# scroll limit bottom pad
# switch pad with n/b
# crypto to own module

H_PAD = 1
LOAD_CRYPTO = True
LOAD_YLE = True
CRYPTOS = ["BTC", "ETH", "AAVE", "MATIC"]


def debugg(joku):
    cs.endwin()
    print(joku)
    sys.exit(0)


def touch_and_refresh(wins):
    for win in wins:
        try:
            wins[win].touchwin()
            wins[win].refresh()
        except Exception:
            debugg(type(win))


def terminate_program(msg=0):
    sys.exit(msg)


def initialize_screen(scr):
    cs.curs_set(0)
    cs.use_default_colors()
    cs.init_pair(1, cs.COLOR_CYAN, -1)
    cs.init_pair(2, cs.COLOR_GREEN, -1)

    max_y, max_x = scr.getmaxyx()
    if max_x < 20:
        msg = "Terminal is too narrow, increase it's width to at least 20"
        terminate_program(msg)
    if max_y < 6:
        msg = "Terminal is too short, increase it's height to at least 6"
        terminate_program(msg)
    return max_y, max_x


def fetch_crypto(cryptos):
    json_data = []
    for coin in cryptos:
        url = "https://api.coinbase.com/v2/prices/" + coin + "-EUR/spot"
        json_data.append(req.get(url).json()["data"])

    return json_data


def print_crypto(win, json):
    max_y, max_x = win.getmaxyx()
    name_length_max = 0
    price_length_max = 0
    for j in json:
        if len(j["base"]) > name_length_max:
            name_length_max = len(j["base"])

        int_amount = str(int(float(j["amount"])))
        if len(int_amount) > price_length_max:
            price_length_max = len(int_amount)

    if name_length_max + price_length_max + 7 > max_x:
        win.addstr(0, 0, "NO ROOM")
        return

    for i in range(len(json)):
        coin = json[i]["base"]
        amount = float(json[i]["amount"])

        header_offset = name_length_max - len(coin)
        header = "{0} {1}".format(coin, (header_offset * ' '))

        amount_offset = price_length_max - len(str(int(amount)))
        amount = "{0}{1:.2f} €".format((amount_offset * ' '), amount)

        win.addstr(i, 0, header, cs.color_pair(1))
        win.addstr(amount, cs.color_pair(2))


def main(stdscr):
    max_y, max_x = initialize_screen(stdscr)

    current_y = 0
    win = {}

    toolbar = cs.newwin(1, max_x, max_y - 1, H_PAD)
    win["toolbar"] = toolbar

    if LOAD_CRYPTO is True:
        crypto_y = len(CRYPTOS) + 1
        crypto_x = max_x - (H_PAD * 2)
        crypto_win = cs.newwin(crypto_y, crypto_x, current_y, H_PAD)
        current_y += crypto_y
        win["crypto"] = crypto_win

    if LOAD_YLE is True:
        yle_y = max_y - current_y - 2
        yle_x = max_x - (H_PAD * 2)
        yle_win = cs.newwin(yle_y, yle_x, current_y, H_PAD)
        yle = yle_module.yle_module(stdscr, yle_win, H_PAD, toolbar)
        win["yle"] = yle

    win["toolbar"].addstr(0, 0, "Initalizing...")
    win["toolbar"].refresh()

    while True:
        if LOAD_CRYPTO is True:
            crypto_json = fetch_crypto(CRYPTOS)
        if LOAD_YLE is True:
            win["yle"].fetch_json()

        if LOAD_CRYPTO is True:
            win["crypto"].erase()
            print_crypto(crypto_win, crypto_json)
            win["crypto"].refresh()
        if LOAD_YLE is True:
            win["yle"].parse_json_data()
            win["yle"].print_data()
            win["yle"].refresh()

        win["toolbar"].erase()
        timer_start = time.perf_counter()
        timer_end = timer_start + 1800
        cs.halfdelay(100)
        while time.perf_counter() < timer_end:
            try:
                key = win["toolbar"].getkey()
            except Exception:
                key = None

            if key == 'u':
                break
            elif key == 'n':
                win["yle"].change_page(1)
                win["yle"].refresh()
            elif key == 'b':
                win["yle"].change_page(-1)
                win["yle"].refresh()
            elif key == 't':
                win["yle"].print_content_pad(0)
                touch_and_refresh(win)
            elif key == 'q':
                terminate_program()
            elif key == 'r':
                cs.echo()
                cs.curs_set(True)
                win["toolbar"].erase()

                prompt = "Page to read: "
                win["toolbar"].addstr(0, 0, prompt)
                input_str = win["toolbar"].getstr(4)

                win["toolbar"].clear()
                win["toolbar"].refresh()
                cs.noecho()
                cs.curs_set(False)

                pad_success = win["yle"].print_content_pad(input_str)
                if pad_success is True:
                    touch_and_refresh(win)
                else:
                    msg = "Invalid article index!"
                    win["toolbar"].addstr(msg)
                    win["toolbar"].refresh()

        win["toolbar"].erase()
        win["toolbar"].addstr(0, 0, "Refreshing...")
        win["toolbar"].refresh()


cs.wrapper(main)
