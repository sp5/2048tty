import sys
import curses
import ani

class All:
    def __init__(self): pass
    def __eq__(self, other):
        return not (other in 'hjkl')
    def __contains__(self, other):
        return not (other in 'hjkl')

ALL = All()

class INeedColorBadly(Exception):
    pass
class RenderingError(Exception):
    pass

class Kuler:
    def __getattr__(self, attr):
        return getattr(curses, "COLOR_"+attr.upper())

class Mover:
    def __init__(self, stack, stdscr, pos):
        self.stk = stack
        self.scr = stdscr
        self.dest = pos

    def __enter__(self):
        y, x = self.scr.getyx()
        self.stk.append(ani.Coord(x, y))
        self.scr.move(*self.dest.rtuple())

    def __exit__(self, *exc_info):
        self.scr.move(*self.stk.pop().rtuple())
        return False


class Terminal:
    def __init__(self):
        c = Kuler()
        self.c = curses
        self.s = curses.initscr()
        curses.start_color()
        if not curses.has_colors():
            raise INeedColorBadly()
        curses.use_default_colors()
        curses.cbreak()
        self.s.keypad(True)
        curses.curs_set(0)
        curses.noecho()
        self.default = 0

        ci = curses.init_pair
        cp = curses.color_pair
        ci(1, c.WHITE, -1);   self.white   = cp(1)
        ci(2, c.CYAN, -1);    self.cyan    = cp(2)
        ci(3, c.BLUE, -1);    self.blue    = cp(3)
        ci(4, c.MAGENTA, -1); self.magenta = cp(4)
        ci(5, c.RED, -1);     self.red     = cp(5)
        ci(6, c.YELLOW, -1);  self.yellow  = cp(6)
        ci(7, c.WHITE, c.BLACK);self.sboxc = cp(7) # score box color

        self.pos_stack = []

    def popup(self, heading,
            bgcolor=curses.COLOR_YELLOW, fgcolor=curses.COLOR_BLACK,
            left="", right="", accept=ALL):
        ssize = self.screen_size()
        curses.init_pair(8, fgcolor, bgcolor)
        mycolor = curses.color_pair(8)
        for i in range(ssize.y - 5, ssize.y):
            for j in range(ssize.x):
                self.s.insch(i, j, " ", mycolor)
        self.write(heading,
                at=ani.Coord(
                    (ssize.x - len(heading)) // 2,
                    ssize.y - 3),
                c=mycolor)
        self.write(left, at=ani.cj * (ssize.y - 1), c=mycolor)
        self.write(right[:-1],
                at=ani.Coord(
                    ssize.x - len(right),
                    ssize.y - 1),
                c=mycolor)
        self.s.insch(ssize.y - 1, ssize.x - 1, right[-1], mycolor)
        while True:
            k = self.getch()
            if k in accept:
                return k



    def done(self):
        curses.curs_set(1)
        self.s.keypad(False)
        curses.nocbreak()
        curses.echo()
        curses.endwin()

    def go(self):
        self.s.refresh()

    def write(self, tx, at=None, c=None):
        try:
            if c is None:
                c = curses.color_pair(0)
            if at:
                ssize = self.screen_size()
                if ani.origin <= at < ssize:
                    if len(tx) > ssize.x - at.x:
                        tx = tx[:ssize.x - at.x]
                    if len(tx) == ssize.x and at.y == ssize.y - 1:
                        self.s.insch(ssize.y - 1, ssize.x - 1,
                                tx[-1], c)
                        tx = tx[:-1]
                    self.s.addstr(int(at.y), int(at.x), tx, c)
                else:
                    print("{}{}".format(
                        at, ssize), file=sys.stderr)
            else:
                self.s.addstr(tx, c)
        except curses.error:
            print("Failed to write | {what} |to| {where} |using| {d}color{cl}|. |{ss}|."
                    .format(
                    what=repr(tx),
                    where=at if at else "cursor", 
                    d="" if c else "default ",
                    cl=(" " + repr(c)) if c else "",
                    ss=self.screen_size()),
                    file=sys.stderr)
#           raise RenderingError(
#               "Failed to write {what} to {where} using {d}color{cl}".format(
#                   what=repr(tx),
#                   where=at if at else "cursor", 
#                   d="" if c else "default ",
#                   cl=(" " + repr(c)) if c else ""))

    def location(self, x=0, y=0):
        return Mover(self.pos_stack, self.s, ani.Coord(x,y))

    def clear(self):
        self.s.erase()

    def getch(self):
        return self.s.getkey()

    def input_flush(self):
        curses.flushinp()

    def screen_size(self):
        y, x = self.s.getmaxyx()
        return ani.Coord(x, y)

