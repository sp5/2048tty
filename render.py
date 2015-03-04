import curses
import ani

class INeedColorBadly(Exception):
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

    def done(self):
        curses.curs_set(1)
        self.s.keypad(False)
        curses.nocbreak()
        curses.endwin()

    def go(self):
        self.s.refresh()

    def write(self, tx, at=None, c=None):
        if c is None:
            c = curses.color_pair(0)
        if at:
            self.s.addstr(at.y, at.x, tx, c)
        else:
            self.s.addstr(tx, c)

    def location(self, x=0, y=0):
        return Mover(self.pos_stack, self.s, ani.Coord(x,y))

    def clear(self):
        self.s.erase()

    def getch(self):
        return self.s.getkey()

    def input_flush(self):
        curses.flushinp()

