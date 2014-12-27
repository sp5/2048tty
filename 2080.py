import blessings, math, random
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
    if len(triples) > 3:
        triples = random.sample(triples, 3)

    for triple in triples:
        grid[triple[0], triple[1]] = Cell(1)

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
    for i, c in enumerate(r):
        if c is not None:
            if new and c == new[-1]:
                new[-1] = Cell(c.power + 1)
            else:
                new.append(c)
    for i in range(len(r)):
        r[i] = new[i] if i < len(new) else None

def main():
    t = blessings.Terminal()
    grid = Grid(x=4, y=4)

    with t.fullscreen():
        tx = input("?")
        while not tx.startswith("q"):

            if tx.startswith('l'):
                for row in grid.rows:
                    pushrow(row)
            elif tx.startswith('r'):
                for row in grid.rows:
                    pushrow(WrapperRev(row))
            elif tx.startswith('u'):
                for col in grid.cols:
                    pushrow(col)
            elif tx.startswith('d'):
                for col in grid.cols:
                    pushrow(WrapperRev(col))
            elif tx.startswith('g'):
                addrand(grid)
            elif tx.startswith('!'):
                import pdb; pdb.set_trace()

            t.stream.write("\x1b[2J\x1b[H")
            for trip in grid.triples:
                if trip.v:
                    trip.v.render(t, 2+trip.y*4, 2+trip.x*7)

            for i, row in enumerate(grid.rows):
                with t.location(x=30, y=2+i):
                    print(repr(row))

            tx = input("?")

if __name__ == '__main__':
    main()
