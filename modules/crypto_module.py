import curses as cs
import requests as req


class crypto_module:
    def __init__(self, win, cryptos):
        self.win = win
        self.cryptos = cryptos
        self.json_data = None

    def refresh(self):
        self.win.refresh()

    def touchwin(self):
        self.win.touchwin()

    def fetch_crypto(self):
        cryptos = self.cryptos
        json_data = []
        for coin in cryptos:
            url = "https://api.coinbase.com/v2/prices/" + coin + "-EUR/spot"
            json_data.append(req.get(url).json()["data"])

        self.json_data = json_data

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
