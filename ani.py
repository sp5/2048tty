import time
from copy import copy

class Coord:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, o):
        return Coord(self.x + o.x, self.y + o.y)

    def __sub__(self, o):
        try:
            return Coord(self.x - o.x, self.y - o.y)
        except AttributeError:
            return Coord(self.x - o, self.y - o)

    def __neg__(self):
        return Coord(-self.x, -self.y)

    def __truediv__(self, o):
        try:
            return Coord(self.x / o.x, self.y / o.y)
        except AttributeError:
            return Coord(self.x / o, self.y / o)

    def __floordiv__(self, o):
        try:
            return Coord(self.x // o.x, self.y // o.y)
        except AttributeError:
            return Coord(self.x // o, self.y // o)

    def __mul__(self, o):
        try:
            return Coord(self.x * o.x, self.y * o.y)
        except AttributeError:
            return Coord(self.x * o, self.y * o)

    def __rmul__(self, o):
        return self * o

    def maxstep(self, ms):
        if self.y == 0:
            if self.x == 0:
                return Coord(0,0)
            else:
                return Coord(ms,0) * self.sign()
        else:
            if self.x == 0:
                return Coord(0,ms) * self.sign()
            else:
                return Coord(ms,ms) * self.sign()

    def sign(self):
        x = 1 if self.x >= 0 else -1
        y = 1 if self.y >= 0 else -1
        return Coord(x, y)
            

    def __repr__(self):
        return "<{0}, {1}>".format(self.x, self.y)

    def astuple(self):
        return self.x, self.y

    def compare(self, o, direction):
        return (
                (self.x - o.x) * direction.x >= 0
               ) and (
                (self.y - o.y) * direction.x >= 0
               )

class Animation:
    pass

class TileMove(Animation):
    def __init__(self, cell, start, end):
        self.start = start # info only
        diff = end - start
        self._step = diff.maxstep(1)
        self.curr = start
        self.end = end
        self.cell = cell

    def render(self, t):
        self.cell.render(t, self.curr.y, self.curr.x)

    def step(self):
        self.curr += self._step

    def done(self):
        return self.curr.compare(self.end, self._step)

    def __repr__(self):
        return "ani.TileMove({0}, {1}, {2})".format(
                repr(self.cell), self.start, self.end)

class TileSpawn(Animation):
    def __init__(self, cell, pos):
        self.pos = pos
        self.stage = 0
        self.cell = cell

    def render(self, t):
        self.cell.render(
                t, self.pos.y + (-1,0,1,0,0)[self.stage],
                self.pos.x + (0,-1,0,1,0)[self.stage])

    def step(self):
        self.stage += 1

    def done(self):
        return self.stage >= 4

    def __repr__(self):
        return "ani.TileSpawn({0}, {1})".format(
                repr(self.cell), self.pos)

def play(t, delay, _animations):
    animations = copy(_animations)

    first = True
    while len(animations) > 0:
        if first:
            first = False
        else:
            time.sleep(delay)
        for animation in animations:
            if animation.done():
                animations.remove(animation)
            else:
                animation.step()
        t.stream.write("\x1b[2J\x1b[H")
        for animation in _animations:
            animation.render(t)
        t.stream.write("\n")

ci = Coord(1, 0)
cj = Coord(0, 1)
