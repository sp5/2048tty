#!/usr/bin/python3
import math, random, sys
import render
from grid import Grid
import ani

class Cell:
    def __init__(self, power):
        self.power = power

    def render(self, t, coord):
        color = ([t.default, t.white, t.cyan, t.blue, t.magenta, t.red]
            [self.power - 1] if self.power < 7 else t.yellow)
        def c(a): t.write(a, c=color)
        with t.location(y=coord.y, x=coord.x):
            c(" ____ ")
        with t.location(y=coord.y + 1, x=coord.x):
            c("/    \\")
        with t.location(y=coord.y + 2, x=coord.x):
            c("\u258c{0}\u2590".format(center(4, 2 ** self.power)))
        with t.location(y=coord.y + 3, x=coord.x):
            c("\\____/")

    def __repr__(self):
        return "Cell({0})".format(self.power)

    def __eq__(self, other):
        return other and self.power == other.power

def center(n, string):
    s = str(string)
    l = len(s)

    p = max(0, n - l)
    pl = math.floor(p / 2)
    pr = math.ceil(p / 2)
    return "".join((" " * pl, s, " " * pr))

def addrand(grid, anims):
    triples = [triple for triple in grid.triples if not triple.v]
    if len(triples) > 1:
        triples = random.sample(triples, 1)

    for triple in triples:
        c = Cell(random.sample([1, 1, 1, 1, 1, 1, 1, 1, 1, 2], 1)[0])
        anims.insert(0, ani.TileSpawn(c, ani.Coord(2+triple.x*7, 2+triple.y*4)))
        grid[triple[0], triple[1]] = c

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

def pushrow(r, cbase, cstep, anims):
    new = []
    previously_combined = False
    for i, c in enumerate(r):
        if c is not None:
            if new and (not previously_combined) and c == new[-1]:
                anims.append(ani.TileMove(
                    c, cbase + i * cstep,
                    cbase + (len(new)-1) * cstep))
                new[-1] = Cell(c.power + 1)
                previously_combined = True
            else:
                anims.append(ani.TileMove(
                    c, cbase + i * cstep,
                    cbase + len(new) * cstep))
                new.append(c)
                previously_combined = False

    if all(x == z for x, z in zip(r, new)):
        return False
    else:
        for i in range(len(r)):
            r[i] = new[i] if i < len(new) else None
        return True

def main():
    t = render.Terminal()
    animationrate = .009
    for arg in sys.argv:
        if arg in ['-h', '--help']:
            t.done()
            import blessings
            t = blessings.Terminal()
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
    {b}!{n} will start a Python debugger.
    Use -A{u}xxx{n} or --animrate{u}xxx{n} to speed up or slow down the
    animations. The default rate is {animrate}.
    """.format(
        b=t.bold, n=t.normal, u=t.underline, animrate=animationrate))
            sys.exit(0)
        elif arg.startswith('-A'):
            animationrate = float(arg[2:])
        elif arg.startswith('--animrate'):
            animationrate = float(arg[len('--animrate'):])


    grid = Grid(x=4, y=4)
    debug = False
    inspect = ani.Coord(0, 0)

    addrand(grid, [])
    addrand(grid, [])
    tx = '_'
    tilesiz = ani.Coord(7, 4)
    stepx = tilesiz * ani.ci
    stepy = tilesiz * ani.cj
    tl = ani.Coord(2, 2)
    anims = None
    while not tx.startswith("q"):
        t.clear()
        for trip in grid.triples:
            if trip.v:
                trip.v.render(t, tl + tilesiz * ani.Coord(trip.x, trip.y))

        if debug:
            for i, row in enumerate(grid.rows):
                t.write(repr(row), at=ani.Coord(30, 2+i))
            for i, anim in enumerate(anims):
                t.write(repr(anim), at=ani.Coord(30, 3+len(grid.rows)+i))
            ic = tl + tilesiz * inspect
            t.write('#', at=ic, c=t.red)
            t.write(repr(ic), at=ani.Coord(30, 3+len(grid.rows)+len(anims)))

        t.go()
        anims = []
        tx = t.getch()
        if tx.startswith('h'):
            ok = []
            for i, row in enumerate(grid.rows):
                ok.append(pushrow(row, tl + stepy * i, stepx, anims))
            if any(ok): addrand(grid, anims)
        elif tx.startswith('l'):
            ok = []
            for i, row in enumerate(grid.rows):
                ok.append(pushrow(
                            WrapperRev(row),
                            tl + stepy*i + stepx*len(grid.rows) - stepx,
                            -stepx, anims))
            if any(ok): addrand(grid, anims)
        elif tx.startswith('k'):
            ok = []
            for i, col in enumerate(grid.cols):
                ok.append(pushrow(col, tl + stepx * i, stepy, anims))
            if any(ok): addrand(grid, anims)
        elif tx.startswith('j'):
            ok = []
            for i, col in enumerate(grid.cols):
                ok.append(pushrow(
                            WrapperRev(col),
                            tl + stepx*i + stepy*len(grid.cols) - stepy,
                            -stepy, anims))
            if any(ok): addrand(grid, anims)
        elif tx.startswith('d'):
            debug = not debug
        elif tx.startswith('!'):
            import pdb
            with t.location():
                t.c.curs_set(1)
                t.c.nocbreak()
                t.s.keypad(False)
                pdb.set_trace()
                t.s.keypad(True)
                t.c.cbreak()
                t.c.curs_set(0)
        elif debug:
            if tx.startswith('H'):
                inspect -= ani.ci
            elif tx.startswith('L'):
                inspect += ani.ci
            elif tx.startswith('K'):
                inspect -= ani.cj
            elif tx.startswith('J'):
                inspect += ani.cj

        t.input_flush()
        ani.play(t, animationrate, anims)
    t.done()

if __name__ == '__main__':
    main()
