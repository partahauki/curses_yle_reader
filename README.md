# curses_yle_reader
Terminal reader for YLE-news (and crypto prices).

Seems to only work on linux. Windows has different curses-library and it seem to conflict somehow.

By default it autorefreshes every 30mins, but this can be changed in the code with the REFRESH_RATE variable.

Dependencies:

- pip install feedparser html2text

Current keybindings (main screen):

- n - next page of news
- b - previous page
- u - manual refresh
- q - quit program
- r - read full article (asks for index)

Article screen:

- j - scroll down
- k - scroll up
- n - next article
- b - previous article
- q - back to main screen

### Crypto prices

If you want to see current prices of crypto-tokens of your choosing, you need to edit start.py a bit. Change LOAD_CRYPTO to True and list all token symbols you wish to keep track of in the array below it. q - back to main screen
