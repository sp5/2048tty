#!/usr/bin/python3

# fixes problems when the game crashes hard and screws up the terminal
# Not needed much now that a finally block is being used
import curses

curses.initscr()
curses.echo()
curses.nocbreak()
curses.curs_set(1)
curses.endwin()
