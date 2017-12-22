#!/usr/bin/python3
import os
import math, random, sys
import render
from grid import Grid
import ani, scorecard
import persist
from abc import ABC, abstractmethod
from collections import namedtuple
from itertools import islice

GAME_WIDTH = 4
GAME_HEIGHT = 4

class EndOfGame(Exception): pass

class CellBase(ABC):
    @abstractmethod
    def get_color(self, t):
        """Returns the color of this tile"""

    def render(self, t, coord):
        _coord = coord
        def c(a, **kw):
            t.write(a, c=self.get_color(t), **kw)
        c(" ____ ", at=coord)
        coord += ani.cj
        c("/    \\", at=coord)
        coord += ani.cj
        c("\u258c    \u2590".format(center(4, self.getnumber())), at=coord)
        self.write_number_only(t, _coord)
        coord += ani.cj
        c("\\____/", at=coord)

    def write_number_only(self, t, coord, truncate=False):
        text = center(4, self.getnumber())
        if truncate:
            text = text[1:-1]
        t.write(text, at=coord + ani.Coord(1, 2), c=self.get_color(t))

    @abstractmethod
    def getnumber(self):
        """Gets the number to be visually displayed"""

    @abstractmethod
    def merge(self, other):
        """Try to merge with other cell, return None if impoossible"""

    @abstractmethod
    def aftermerge(self):
        """Return the likely result of merge with a compatible cell"""

class Cell(CellBase):
    def __init__(self, power):
        self.power = power

    def get_color(self, t):
        colors = [t.red, t.default, t.white, t.cyan, t.blue, t.magenta, t.red]
        if self.power < 7:
            return colors[self.power]
        else:
            return t.yellow

    def getnumber(self):
        return str(2 ** self.power)

    def __repr__(self):
        return "Cell({0})".format(self.power)

    def __eq__(self, other):
        return other and self.power == other.power

    def merge(self, other):
        if self.power == other.power:
            return Cell(self.power + 1)

    def aftermerge(self):
        return Cell(self.power + 1)

class Threes1Cell(CellBase):
    def __init__(self):
        pass

    def get_color(self, t):
        return t.blue

    def getnumber(self):
        return '1'

    def __repr__(self):
        return "Threes1Cell()"

    def __eq__(self, other):
        return other and isinstance(other, type(self))

    def merge(self, other):
        if isinstance(other, Threes2Cell):
            return ThreesLargeCell(0)

    def tojson(self):
        return 0

    def aftermerge(self):
        return ThreesLargeCell(0)

class Threes2Cell(CellBase):
    def __init__(self):
        pass

    def get_color(self, t):
        return t.red

    def getnumber(self):
        return '2'

    def __repr__(self):
        return "Threes2Cell()"

    def __eq__(self, other):
        return other and isinstance(other, type(self))

    def merge(self, other):
        if isinstance(other, Threes1Cell):
            return ThreesLargeCell(0)

    def tojson(self):
        return 1

    def aftermerge(self):
        return ThreesLargeCell(0)


class ThreesLargeCell(CellBase):
    def __init__(self, x3):
        self.x3 = x3

    def get_color(self, t):
        return t.white

    def getnumber(self):
        return 3 * 2 ** self.x3

    def __repr__(self):
        return "ThreesLargeCell({0})".format(self.x3)

    def __eq__(self, other):
        return other and isinstance(other, type(self)) and self.x3 == other.x3

    def merge(self, other):
        if isinstance(other, ThreesLargeCell) and self.x3 == other.x3:
            return ThreesLargeCell(self.x3 + 1)

    def tojson(self):
        return self.x3 - 2

    def aftermerge(self):
        return ThreesLargeCell(self.x3 + 1)


def center(n, string):
    s = str(string)
    l = len(s)

    p = max(0, n - l)
    pl = math.floor(p / 2)
    pr = math.ceil(p / 2)
    return "".join((" " * pl, s, " " * pr))

def addrand(grid):
    anims = []
    triples = [triple for triple in grid.triples if not triple.v]
    if len(triples) > 1:
        triples = random.sample(triples, 1)

    for triple in triples:
        c = Cell(random.sample([1, 1, 1, 1, 1, 1, 1, 1, 1, 2], 1)[0])
        anims.insert(0, ani.TileSpawn(c, ani.Coord(2+triple.x*7, 2+triple.y*4)))
        grid[triple[0], triple[1]] = c

    return anims

def addrandthrees(grid):
    anims = []

    triples = [triple for triple in grid.triples if not triple.v]
    if len(triples) > 1:
        triples = random.sample(triples, 1)

    for triple in triples:
        c = random.sample([Threes1Cell, Threes2Cell], 1)[0]()
        anims.insert(0, ani.TileSpawn(c, ani.Coord(2+triple.x*7, 2+triple.y*4)))
        grid[triple[0], triple[1]] = c
    return anims


class WrapperRev:
    # TODO: This whole class is buggered up and possibly unnecessary. Maybe
    # replace with builtin reversed?
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

# FIXME
def pushrow(r, cbase, cstep, anims, score):
    new = []
    previously_combined = False
    for i, c in enumerate(r):
        if c is not None:
            if new and (not previously_combined) and c == new[-1]:
                anims.append(ani.TileMove(
                    c, cbase + i * cstep,
                    cbase + (len(new)-1) * cstep,
                    merge=True))
                new[-1] = Cell(c.power + 1)
                score.diff += 2 ** (c.power + 1)
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

def pushrowv2(row, cbase, cstep):
    anims = []
    score = Score()
    moved_any = pushrow(row, cbase, cstep, anims, score)
    return moved_any, score.diff, anims

def pushrowthrees(row, cbase, cstep):
    anims = []
    moved_any = False

    for i in range(1, len(row)):
        c = row[i]
        if not c: continue
        assert i >= 1, "I is {!r}".format(i)
        prev = row[i - 1]

        if not prev:
            row[i - 1] = c
            row[i] = None
            anims.append(ani.TileMove(
                c, cbase + i * cstep,
                cbase + (i - 1) * cstep))
            moved_any = True
        else:
            m = c.merge(prev)
            if m:
                row[i - 1] = m
                row[i] = None
                anims.append(ani.TileMove(
                    c, cbase + i * cstep,
                    cbase + (i - 1) * cstep, merge=True))
                moved_any = True
    return moved_any, 0, anims

class Score:
    def __init__(self, score=0, hiscore=0):
        self.score = score
        self.hiscore = hiscore
        self.diff = 0

def post_win(grid):
    for triple in grid.triples:
        if triple.v and triple.v.power >= 11:
            return True
    return False

def post_win_threes(grid):
    return False

def moves_possible(grid):
    for triple in grid.triples:
        if triple.v == None:
            return True
    
    for row in grid.rows:
        for i in range(len(row) - 1):
            if row[i].merge(row[i+1]):
                return True
    for col in grid.cols:
        for i in range(len(col) - 1):
            if col[i].merge(col[i+1]):
                return True

DEFAULT_KEY_BINDINGS = {
    'h': ('h', 'KEY_LEFT'),
    'l': ('l', 'KEY_RIGHT'),
    'j': ('j', 'KEY_DOWN'),
    'k': ('k', 'KEY_UP'),
    'q': ('q', '\x1b'),
    'x': ('x',),
    'd': tuple(),
    'H': ('H',),
    'J': ('J',),
    'K': ('K',),
    'L': ('L',),
    '0': ('0',),
    '1': ('1',),
    '2': ('2',),
    '3': ('3',),
    '4': ('4',),
    '5': ('5',),
    '6': ('6',),
    '7': ('7',),
    '8': ('8',),
    '9': ('9',),
    '+': ('+',),
    '-': ('-',),
}

class GameBase(ABC):
    def __init__(self, per):
        self.per = per
        self.debug = False
        self.inspect = ani.Coord(0, 0)
        self.animationrate = .009
        self.readargs(t)

        self.grid = Grid(x=GAME_WIDTH, y=GAME_HEIGHT)
        self.tilesiz = ani.Coord(7, 4)
        self.stepx = self.tilesiz * ani.ci
        self.stepy = self.tilesiz * ani.cj
        self.tl = ani.Coord(2, 2)

        self.init_game()

    def run(self, t):
        return self.main(t)

    LEFT = 0x00
    RIGHT = 0x01
    UP = 0x10
    DOWN = 0x11

    @abstractmethod
    def pushrowv2(self, *args):
        pass

    def push(self, direction):
        rev = direction in (self.RIGHT, self.DOWN)
        vert = direction in (self.UP, self.DOWN)

        if vert:
            s0, s1 = self.stepx, self.stepy
            rows = self.grid.cols
        else:
            s0, s1 = self.stepy, self.stepx
            rows = self.grid.rows

        ok = []
        anims = []
        newscore = 0
        for i, row in enumerate(rows):
            if rev:
                cbase = self.tl + s0*i + s1*len(rows) - s1
                cstep = -s1
                row = WrapperRev(row)
            else:
                cbase = self.tl + s0 * i
                cstep = s1

            moved_any, upscore, newanims = self.pushrowv2(row, cbase, cstep)
            ok.append(moved_any)
            newscore += upscore
            anims.extend(newanims)

        return any(ok), newscore, anims

    @abstractmethod
    def addrand(self, l=None, grid=None):
        pass

    @abstractmethod
    def loadcell(self, cellval):
        pass

    @abstractmethod
    def post_win(self):
        pass

    def init_game(self):
        self.score   = 0
        self.hiscore = self.per["hiscore"]
        if "savegame" in self.per:
            for i, row in enumerate(self.per["savegame"]):
                for j, cell in enumerate(row):
                    self.grid[j,i] = self.loadcell(cell) if cell else None
            self.won_already = self.post_win()
            if "score" in per:
                self.score = self.per["score"]
        else:
            self.addrand()
            self.addrand()
            self.won_already = False

        self.keybinds = DEFAULT_KEY_BINDINGS.copy()
        if "keybinds" in self.per:
            for kbname, kbset in self.per["keybinds"].items():
                self.keybinds[kbname] = kbset
        self.update_reverse_keybinds()

    def update_reverse_keybinds(self):
        self.reverse_keybinds = {}
        for kbname, kbset in self.keybinds.items():
            for key in kbset:
                self.reverse_keybinds[key] = kbname

    def nextaction(self, t):
        while True:
            key = t.getch()
            if key in self.reverse_keybinds:
                return self.reverse_keybinds[key]

    @abstractmethod
    def savecell(self, cell):
        pass

    def main(self, t):
        per = self.per

        tx = '_' # tx is the current action
        anims = None
        while not tx.startswith("q"):
            t.clear()
            # main grid
            for trip in self.grid.triples:
                if trip.v:
                    trip.v.render(t, self.tl +
                            self.tilesiz * ani.Coord(trip.x, trip.y))
            # score card
            score_diff = 0
            scorecard.draw(t, self.tl + self.tilesiz * ani.ci * 4 +
                    ani.Coord(10, 5), self.score, self.hiscore)
            # check if the game was won on the last turn
            if self.post_win() and not self.won_already:
                self.won_already = True
                k = t.popup("YOU WON!",
                        left="press c to continue", right="press q to quit",
                        accept="cq")
                if k == 'c':
                    continue
                elif k == 'q':
                    per["hiscore"] = max(per["hiscore"], self.hiscore)
                    del per["savegame"]
                    del per["score"]
                    raise EndOfGame()

            if not moves_possible(self.grid):
                t.popup("YOU LOST", right="press any key to quit",
                        bgcolor=t.c.COLOR_WHITE)
                break
            # debug
            if self.debug:
                for i, row in enumerate(self.grid.rows):
                    t.write(repr(row), at=ani.Coord(30, 2+i))
                for i, anim in enumerate(anims):
                    t.write(repr(anim), at=ani.Coord(30,
                        3 + len(self.grid.rows) + i))
                ic = self.tl + self.tilesiz * self.inspect
                t.write('#', at=ic, c=t.red)
                t.write(repr(ic), at=ani.Coord(30,
                    3 + len(self.grid.rows) + len(anims)))

            # refresh screen
            t.go()
            # clear anims
            anims = []
            # get & process input
            tx = self.nextaction(t)
            # movement
            if tx.startswith('h'):
                ok, upscore, newanims = self.push(self.LEFT)
                anims.extend(newanims)
                score_diff += upscore
                if ok: anims.extend(self.addrand())
            elif tx.startswith('l'):
                ok, upscore, newanims = self.push(self.RIGHT)
                anims.extend(newanims)
                score_diff += upscore
                if ok: anims.extend(self.addrand())
            elif tx.startswith('k'):
                ok, upscore, newanims = self.push(self.UP)
                anims.extend(newanims)
                score_diff += upscore
                if ok: anims.extend(self.addrand())
            elif tx.startswith('j'):
                ok, upscore, newanims = self.push(self.DOWN)
                anims.extend(newanims)
                score_diff += upscore
                if ok: anims.extend(self.addrand())
            # quit w/o saveing
            elif tx.startswith('x'):
                k = t.popup(
                        "Are you sure you want to quit and clear the board?",
                        right="press y to confirm", bgcolor=t.c.COLOR_MAGENTA)
                if k == 'y':
                    del per["savegame"]
                    del per["score"]
                    raise EndOfGame()
            # debug mode
            elif tx.startswith('d'):
                self.debug = not self.debug
            # start pdb if things are really bad
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
            elif self.debug:
                # move location indicator
                if tx.startswith('H'):
                    self.inspect -= ani.ci
                elif tx.startswith('L'):
                    self.inspect += ani.ci
                elif tx.startswith('K'):
                    self.inspect -= ani.cj
                elif tx.startswith('J'):
                    self.inspect += ani.cj
                elif tx.isdigit():
                    self.grid[self.inspect.x, self.inspect.y] = Cell(int(tx))
                elif tx == '+':
                    self.grid[self.inspect.x, self.inspect.y] = Cell(
                        self.grid[self.inspect.x, self.inspect.y].power + 1)
                elif tx == '-':
                    self.grid[self.inspect.x, self.inspect.y] = Cell(
                        self.grid[self.inspect.x, self.inspect.y].power - 1)
            self.score += score_diff
            self.hiscore = max(self.score, self.hiscore)
            anims.append(scorecard.ScoreCardAnim(
                    score_diff,
                    self.tl + self.tilesiz * ani.ci * 4 + ani.Coord(10, 5),
                    self.score, self.hiscore))
            # don't want any suprise motions
            t.input_flush()

            ani.play(t, self.animationrate, anims)
        per["hiscore"] = max(per["hiscore"], self.hiscore)
        if moves_possible(self.grid):
            per["savegame"] = [
                    [self.savecell(c) if c else None for c in r] for r in self.grid.rows]
            per["score"] = self.score
        else:
            del per["savegame"]
            del per["score"]

    def readargs(self, t):
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

    The game's high score is soted in ~/.2048tty by default. You can change
    this location be setting the 2048TTY_FILE environment varible.
""".format(
            b=t.bold, n=t.normal, u=t.underline, animrate=self.animationrate))
                sys.exit(0)
            elif arg.startswith('-A'):
                self.animationrate = float(arg[2:])
            elif arg.startswith('--animrate'):
                self.animationrate = float(arg[len('--animrate'):])

class Game(GameBase):
    def pushrowv2(self, *args):
        return pushrowv2(*args)

    def addrand(self, grid=None):
        if not grid: grid = self.grid
        return addrand(grid)

    def loadcell(self, cellval):
        return Cell(cellval)

    def post_win(self):
        return post_win(self.grid)

    def savecell(self, cell):
        return cell.power

class GameThrees(GameBase):
    def pushrowv2(self, *args):
        return pushrowthrees(*args)

    def addrand(self, l=None, grid=None):
        if not grid: grid = self.grid
        return addrandthrees(grid)

    def loadcell(self, cellval):
        if cellval == 0:
            return Threes1Cell()
        elif cellval == 1:
            return Threes2Cell()
        else:
            return ThreesLargeCell(cellval - 2)

    def post_win(self):
        return post_win_threes(self.grid)

    def savecell(self, cell):
        return cell.tojson()

if __name__ == '__main__':
    per = persist.Persister()
    t = render.Terminal()
    try:
        if os.getenv('GAMETYPE') == 'THREES':
            game = GameThrees(per)
        else:
            game = Game(per)
        game.run(t)
    except EndOfGame:
        pass
    finally:
        t.done()
        per.finish()
        print("Cleaned up")
