#!/usr/bin/python3
import math, random, sys
import curses, blessings
from grid import Grid

class Cell:
    def __init__(self, power):
        self.power = power

    def render(self, t, y, x):
        color = ([t.default, t.white, t.cyan, t.blue, t.magenta, t.red]
            [self.power - 1] if self.power < 7 else t.yellow)
        def c(a):
            t.stream.write(color + a + t.normal)
        with t.location(y=y, x=x):
            c(" ____ ")
        with t.location(y=y + 1, x=x):
            c("/    \\")
        with t.location(y=y + 2, x=x):
            c("\u258c{0}\u2590".format(center(4, 2 ** self.power)))
        with t.location(y=y + 3, x=x):
            c("\\____/")

    def __repr__(self):
        return "Cell({0})".format(self.power)

    def __eq__(self, other):
        return self.power == other.power

def center(n, string):
    s = str(string)
    l = len(s)

    p = max(0, n - l)
    pl = math.floor(p / 2)
    pr = math.ceil(p / 2)
    return "".join((" " * pl, s, " " * pr))

def addrand(grid):
    triples = [triple for triple in grid.triples if not triple.v]
    if len(triples) > 1:
        triples = random.sample(triples, 1)

    for triple in triples:
        grid[triple[0], triple[1]] = Cell(random.sample([1, 1, 1, 2], 1)[0])

class WrapperRev:
    def __init__(self, l):
        self.l = l

    def __getitem__(self, i):
        return self.l[len(self.l) - i - 1]

    def __setitem__(self, i, n):
        self.l[len(self.l) - i - 1] = n

    def __iter__(self):
        i = 0
        while i < len(self):
            yield self[i]
            i += 1

    def __len__(self):
        return len(self.l)

def pushrow(r):
    new = []
    previously_combined = False
    for i, c in enumerate(r):
        if c is not None:
            if new and (not previously_combined) and c == new[-1]:
                new[-1] = Cell(c.power + 1)
                previously_combined = True
            else:
                new.append(c)
                previously_combined = False

    for i in range(len(r)):
        r[i] = new[i] if i < len(new) else None

def main():
    t = blessings.Terminal()
    for arg in sys.argv:
        if arg in ['-h', '--help']:
            print("""{b}2048{n}
Implementation in python by Samuel Phillips <samuel.phillips29@gmail.com>
Based on 2048 by Gabriele Cirulli. <gabrielecirulli.com>
To play:
    Use hjkl to push the tiles:
              ^
        < {b}h j k l{n} >
            v

    The objective is to combine tiles to form a 2048 tile.
    Press {b}q{n} to quit.
    {b}!{n} will start a Python debugger.""".format(
        b=t.bold, n=t.normal))
            sys.exit(0)

    grid = Grid(x=4, y=4)
    stdscr = curses.initscr()
    curses.cbreak()
    debug = False

    tx = chr(stdscr.getch())
    while not tx.startswith("q"):

        if tx.startswith('h'):
            for row in grid.rows:
                pushrow(row)
            addrand(grid)
        elif tx.startswith('l'):
            for row in grid.rows:
                pushrow(WrapperRev(row))
            addrand(grid)
        elif tx.startswith('k'):
            for col in grid.cols:
                pushrow(col)
            addrand(grid)
        elif tx.startswith('j'):
            for col in grid.cols:
                pushrow(WrapperRev(col))
            addrand(grid)
        elif tx.startswith('d'):
            debug = not debug
        elif tx.startswith('!'):
            import pdb; pdb.set_trace()

        t.stream.write("\x1b[2J\x1b[H")
        for trip in grid.triples:
            if trip.v:
                trip.v.render(t, 2+trip.y*4, 2+trip.x*7)

        if debug:
            for i, row in enumerate(grid.rows):
                with t.location(x=30, y=2+i):
                    print(repr(row))

        print()
        tx = chr(stdscr.getch())
    curses.endwin()

if __name__ == '__main__':
    main()
