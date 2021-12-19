import curses as cs
import math
import sys
from datetime import datetime
import html2text
import feedparser as fp
from utils import string_utils as str_ut

h2t = html2text.HTML2Text()
h2t.ignore_links = True
h2t.ignore_images = True


class yle_module:
    def __init__(self, max_y, max_x, begin_y, h_pad, scr_max_y, scr_max_x):
        self.max_x = max_x
        self.max_y = max_y
        self.begin_y = begin_y
        self.h_pad = h_pad
        self.scr_max_y = scr_max_y
        self.scr_max_x = scr_max_x

        self.win = cs.newwin(max_y, max_x, begin_y, h_pad)
        self.pad = cs.newpad(1, 1)
        self.json_data = None
        self.current_page = 0
        self.page_data = None
        self.content_data = None

        h2t.body_width = scr_max_x - h_pad * 2
        self._flag_no_room = False

    def debugg(self, joku):
        cs.endwin()
        print(joku)
        sys.exit(0)

    def refresh(self):
        self.win.refresh()

    def touchwin(self):
        self.win.touchwin()

    def fetch_json(self):
        url = "https://feeds.yle.fi/uutiset/v1/majorHeadlines/YLE_UUTISET.rss"
        self.json_data = fp.parse(url)

    def parse_json_data(self):
        json_data = self.json_data
        max_y, max_x = self.win.getmaxyx()
        page_data = [[]]
        content_data = []
        page_counter = 0
        y_counter = 1
        for i in range(len(json_data.entries)):
            try:
                content = json_data.entries[i]["content"][0]["value"]
                content_data.append(h2t.handle(content))
            except KeyError:
                id_ = json_data.entries[i]["id"]
                content = "No text-based content provided, see full article a"
                "t " + id_
                content_data.append(content)

            timestamp = json_data.entries[i]["published"]
            timestamp = datetime.strptime(timestamp, "%a, %d %b %Y %X %z")
            timestamp = datetime.strftime(timestamp, "%d.%m %X")
            y_timestamp = y_counter
            rows_timestamp = 1
            y_counter += rows_timestamp

            headline = json_data.entries[i]["title"]
            headline = str_ut.fit_text_to_rows(headline, max_x)
            y_headline = y_counter
            rows_headline = math.ceil(len(headline)/max_x)
            y_counter += rows_headline

            desc = json_data.entries[i]["summary"]
            desc = str_ut.fit_text_to_rows(desc, max_x)
            y_desc = y_counter
            rows_desc = math.ceil(len(desc)/max_x)
            y_counter += rows_desc

            if y_counter > max_y:
                if i == 0:
                    self._flag_no_room = True
                    return
                page_counter += 1
                page_data.append([])
                y_counter = 1 + rows_headline + rows_desc + rows_timestamp
                y_timestamp = 1
                y_headline = 1 + rows_timestamp
                y_desc = 1 + rows_headline + rows_timestamp

            news_data = {
                "index": i,
                "y_timestamp": y_timestamp,
                "timestamp": timestamp,
                "y_headline": y_headline,
                "headline": headline,
                "y_desc": y_desc,
                "desc": desc
            }
            page_data[page_counter].append(news_data)
            y_counter += 1
        self.page_data = page_data
        self._flag_no_room = False
        self.content_data = content_data

    def print_data(self):
        self.win.erase()
        page_number = self.current_page
        if self._flag_no_room is True:
            self.win.addstr(0, 0, "NO ROOM")
            return

        header = "UUTISET ({0}/{1}):".format(page_number + 1,
                                             len(self.page_data))
        self.win.addstr(0, 0, header)

        for news in self.page_data[page_number]:
            prefix = "({0}) ".format(news["index"] + 1)
            self.win.addstr(news["y_timestamp"], 0, prefix + news["timestamp"])
            self.win.addstr(news["y_headline"], 0, news["headline"],
                            cs.color_pair(1))
            self.win.addstr(news["y_desc"], 0, news["desc"])

    def change_page(self, pages_forward):
        self.current_page += pages_forward
        if self.current_page >= len(self.page_data):
            self.current_page = 0
        elif self.current_page < 0:
            self.current_page = len(self.page_data) - 1
        self.print_data()

    def print_content_pad(self, news_i):
        pad = self.pad
        content = self.content_data[news_i]
        pad_length = math.ceil(len(content)/self.max_x)
        pad.resize(pad_length+1000, self.max_x)
        str_ut.curses_print_markdown(pad, content)

        h_pad = self.h_pad
        scr_max_y = self.scr_max_y - 3
        scr_max_x = self.scr_max_x
        pad.refresh(0, 0, 0, h_pad, scr_max_y, scr_max_x)

        pad_position = 0
        while True:
            try:
                key = pad.getkey()
            except Exception:
                key = None

            if pad_position < 0:
                pad_position = 0
            elif pad_position > pad_length:
                # pad_position = pad_length
                pass

            if key == 'j':
                pad_position += 1
                pad.refresh(pad_position, 0, 0, h_pad, scr_max_y, scr_max_x)
            elif key == 'k':
                pad_position += -1
                pad.refresh(pad_position, 0, 0, h_pad, scr_max_y, scr_max_x)
            elif key == 'q':
                break

        pad.clear()
