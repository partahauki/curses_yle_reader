import curses as cs


class toolbar_module:
    def __init__(self, win):
        self.win = win

    def refresh(self):
        self.win.refresh()

    def touchwin(self):
        self.win.touchwin()

    def take_input(self, prompt):
        win = self.win
        max_y, max_x = win.getmaxyx()
        input_max_x = max_x - len(prompt)

        cs.echo()
        cs.curs_set(True)
        win.erase()

        win.addstr(0, 0, prompt)
        input_str = win.getstr(input_max_x)

        win.clear()
        win.refresh()
        cs.noecho()
        cs.curs_set(False)

        return input_str
