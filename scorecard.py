import render
import ani
def draw(t, pos, score, highscore):
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
        self.dpos = pos - ani.cj # position of +12, etc.
        self.diff = "+{}".format(diff) if diff > 0 else None
        self.args = args
        self.kwargs = kwargs

    def render(self, t):
        draw(t, self.pos, *self.args, **self.kwargs)
        if self.diff:
            t.write(self.diff, at=self.dpos, c=t.magenta)

    def step(self):
        self.dpos -= ani.cj

    def done(self):
        return True

    def __repr__(self):
        return "ani.ScoreCardAnim({0}, {1})".format(self.args, self.kwargs)
