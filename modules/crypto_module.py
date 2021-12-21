import sys
import math
import curses as cs
import requests as req


class crypto_module:
    def __init__(self, win, cryptos):
        self.win = win
        self.cryptos = cryptos
        self.json_data = None

    def debugg(self, joku):
        cs.endwin()
        print(joku)
        sys.exit(0)

    def refresh(self):
        self.win.refresh()

    def touchwin(self):
        self.win.touchwin()

    def adjust_win_height(self):
        max_y, max_x = self.win.getmaxyx()
        self.fetch_crypto()
        columns = self._calculate_columns(self.win, self.json_data)
        win_height = math.ceil(len(self.cryptos)/columns) + 1
        self.win.resize(win_height, max_x)

        return win_height

    def fetch_crypto(self):
        cryptos = self.cryptos
        json_data = []
        for coin in cryptos:
            url = "https://api.coinbase.com/v2/prices/" + coin + "-EUR/spot"
            json_data.append(req.get(url).json()["data"])

        self.json_data = json_data

    def _calculate_max_len(self, json, detailed=None):
        name_length_max = 0
        price_length_max = 0
        for j in json:
            if len(j["base"]) > name_length_max:
                name_length_max = len(j["base"])

            int_amount = str(int(float(j["amount"])))
            if len(int_amount) > price_length_max:
                price_length_max = len(int_amount)

        max_len = name_length_max + price_length_max + 8

        if detailed is None:
            return max_len
        else:
            return max_len, name_length_max, price_length_max

    def _calculate_columns(self, win, json):
        max_y, max_x = win.getmaxyx()
        max_len = self._calculate_max_len(json)
        columns = max_x // max_len

        return columns

    def print_crypto(self):
        json = self.json_data
        win = self.win

        win.erase()
        max_y, max_x = win.getmaxyx()

        columns = self._calculate_columns(win, json)

        if self._calculate_max_len(json) > max_x:
            win.addstr(0, 0, "NO ROOM")
            return

        column_map = []
        for i in range(columns):
            column_map.append([])

        column_i = 0
        for j in json:
            column_map[column_i].append(j)
            if column_i != len(column_map) - 1:
                column_i += 1
            else:
                column_i = 0

        begin_column_x = 0
        for column in column_map:
            max_len, name_len, price_len = self._calculate_max_len(column, 1)
            row_i = 0
            for entry in column:
                coin = entry["base"]
                amount = float(entry["amount"])

                header_offset = name_len - len(coin)
                header = "{0} {1}".format(coin, (header_offset * ' '))

                amount_offset = price_len - len(str(int(amount)))
                amount = "{0}{1:.2f} €".format((amount_offset * ' '), amount)

                win.addstr(row_i, begin_column_x, header, cs.color_pair(1))
                win.addstr(amount, cs.color_pair(2))

                row_i += 1
            begin_column_x += max_len

    """
    def print_crypto(self):
        json = self.json_data
        win = self.win
        win.erase()
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
    """
