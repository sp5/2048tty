import sys
import render
import ani
def draw(t, pos, score, highscore):
#   print("Scorecard draw at {0}".format(pos), file=sys.stderr)
    t.write("-Score----", at=pos + ani.Coord(0, 0), c=t.sboxc)
    t.write(         "|", at=pos + ani.Coord(9, 1), c=t.sboxc)
    t.write("|"         , at=pos + ani.Coord(0, 1), c=t.sboxc)
    t.write( str(score) , at=pos + ani.Coord(1, 1), c=t.yellow)
    t.write("-High-----", at=pos + ani.Coord(0, 2), c=t.sboxc)
    t.write(         "|", at=pos + ani.Coord(9, 3), c=t.sboxc)
    t.write("|"         , at=pos + ani.Coord(0, 3), c=t.sboxc)
    t.write( str(highscore), at=pos + ani.Coord(1, 3),
            c=t.yellow if highscore > score else t.red)
    t.write("----------", at=pos + ani.Coord(0, 4), c=t.sboxc)

class ScoreCardAnim(ani.Animation):
    def __init__(self, diff, pos, *args, **kwargs):
        self.pos = pos
        self.dpos = pos + ani.Coord(1, 2) # position of +12, etc.
        self.diff = "+{}".format(diff) if diff > 0 else None
        self.args = args
        self.kwargs = kwargs

    def render(self, t):
        draw(t, self.pos, *self.args, **self.kwargs)
        if self.diff:
#           print("Writing at {0}".format(self.dpos), file=sys.stderr)
            t.write(self.diff, at=self.dpos, c=t.magenta)

    def step(self):
        self.dpos -= ani.cj * .25

    def done(self):
        return  self.dpos.y < self.pos.y - 1 if self.diff else True

    def __repr__(self):
        return "ani.ScoreCardAnim({0}, {1} <{2}>)".format(
                self.args, self.kwargs, self.dpos)
