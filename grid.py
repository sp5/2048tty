class Triple:
    def __init__(self, x, y, v):
        self.x = x
        self.y = y
        self.v = v

    def __getitem__(self, n):
        return [self.x, self.y, self.v][n]

    def __len__(self):
        return 3

    def __iter__(self):
        return iter([self.x, self.y, self.v])

    def __repr__(self):
        return 'Triple({0}, {1}, {2})'.format(self.x, self.y, self.v)

class Triples:
    def __init__(self, grid):
        self.grid = grid

    def __iter__(self):
        for y in range(self.grid.height):
            for x in range(self.grid.width):
                yield Triple(x, y, self.grid[x, y])

    def __repr__(self):
        return '[{0}]'.format(", ".join(repr(i) for i in self))

class Row:
    def __init__(self, grid, y):
        self.y = y
        self.grid = grid

    def __getitem__(self, x):
        return self.grid[x, self.y]

    def __setitem__(self, x, n):
        self.grid[x, self.y] = n

    def __len__(self):
        return self.grid.width

    def __iter__(self):
        i = 0
        while i < len(self):
            yield self[i]
            i += 1

    def __repr__(self):
        return '[{0}]'.format(", ".join(repr(i) for i in self))

class Rows:
    def __init__(self, grid):
        self.grid = grid

    def __getitem__(self, y):
        return Row(self.grid, y)

    def __len__(self):
        return self.grid.height

    def __iter__(self):
        i = 0
        while i < len(self):
            yield self[i]
            i += 1

    def __repr__(self):
        return '[{0}]'.format(", ".join(repr(i) for i in self))

class Col:
    def __init__(self, grid, x):
        self.x = x
        self.grid = grid

    def __getitem__(self, y):
        return self.grid[self.x, y]

    def __setitem__(self, y, n):
        self.grid[self.x, y] = n

    def __len__(self):
        return self.grid.height

    def __iter__(self):
        i = 0
        while i < len(self):
            yield self[i]
            i += 1

    def __repr__(self):
        return '[{0}]'.format(", ".join(repr(i) for i in self))

class Cols:
    def __init__(self, grid):
        self.grid = grid

    def __getitem__(self, x):
        return Col(self.grid, x)

    def __len__(self):
        return self.grid.width

    def __iter__(self):
        i = 0
        while i < len(self):
            yield self[i]
            i += 1

    def __repr__(self):
        return '[{0}]'.format(", ".join(repr(i) for i in self))

class Grid:
    def __init__(self, x=0, y=0):
        self.data = [None for _ in range(x * y)]
        self.width = x
        self.height = y
        self.rows = Rows(self)
        self.cols = Cols(self)
        self.triples = Triples(self)

    def __getitem__(self, x_y):
        x, y = x_y
        return self.data[self.width * y + x]

    def __setitem__(self, x_y, nval):
        x, y = x_y
        self.data[self.width * y + x] = nval

    def __repr__(self):
        return "<Grid(x={0}, y={1}) {2}>".format(
                self.width, self.height, self.data)
