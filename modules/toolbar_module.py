import curses as cs


class toolbar_module:
    def __init__(self, win, scr_max_y, scr_max_x):
        self.win = win
        self.scr_max_y = scr_max_y
        self.scr_max_x = scr_max_x

    def refresh(self):
        self.win.refresh()

    def touchwin(self):
        self.win.touchwin()

    def resize_window(self, new_x, new_y, h_pad):
        self.win.resize(2, new_x-(h_pad*2))
        self.win.mvwin(new_y - 2, h_pad)

    def take_input(self, prompt):
        win = self.win
        max_y, max_x = win.getmaxyx()
        input_max_x = max_x - len(prompt)

        cs.echo()
        cs.curs_set(True)
        win.erase()

        win.addstr(1, 0, prompt)
        input_str = win.getstr(input_max_x)

        win.clear()
        win.refresh()
        cs.noecho()
        cs.curs_set(False)

        return input_str
