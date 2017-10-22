#!/usr/bin/python3
import unittest
from grid import Grid
import ani
import py2048
from py2048 import Cell

def mkgrid(*nums):
    g = Grid(x=4, y=4)
    for y in range(4):
        for x in range(4):
            n = nums[x + 4 * y]
            g[x, y] = py2048.Cell(n) if n else n
    return g


class AddRandTests(unittest.TestCase):
    def test_addrand(self):
        grid = mkgrid(
                None, None, None, None,
                4,    5,    None, None,
                None, 1,    None, 2,
                None, None, 4,    None)
        anims = []
        py2048.addrand(grid, anims)

        self.assertEqual(len(anims), 1)

class PushRowTests(unittest.TestCase):
    def test_pushrow(self):
        row = [None, Cell(1), Cell(1), Cell(2)]
        anims = []
        cbase = ani.Coord(1, 1)
        cstep = ani.Coord(1, 1)
        score = py2048.Score()

        result = py2048.pushrow(row, cbase, cstep, anims, score)
        self.assertTrue(result)
        self.assertEqual(row[0], Cell(2))
        self.assertEqual(row[1], Cell(2))
        self.assertEqual(row[2], None)
        self.assertEqual(row[3], None)
        self.assertEqual(score.diff, 4)
        self.assertEqual(len(anims), 3)

if __name__ == '__main__':
    unittest.main()
