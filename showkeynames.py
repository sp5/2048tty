#!/usr/bin/python3
import render
import itertools
from ani import Coord as co, ci, cj

def run(t):
    keynames = []

    while True:
        ss = t.screen_size()
        t.clear()
        for i, keyname in enumerate(itertools.islice(reversed(keynames), ss.y -
            4)):
            t.write(repr(keyname), at=co(2, 2) + i * cj)

        t.write("Press k twice to exit", at = ss*ci - 20*ci, c=t.yellow)

        tx = t.getch()

        if keynames and keynames[-1] == 'k' and tx == 'k':
            return
        keynames.append(tx)

if __name__ == '__main__':
    t = render.Terminal()
    try:
        run(t)
    finally:
        t.done()
