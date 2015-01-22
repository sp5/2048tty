getch = None

try:
    import tty, sys, termios
    def _getch():
        fdin = sys.stdin.fileno()
        oldtc = termios.tcgetattr(fdin)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fdin, termios.TCSADRAIN, oldtc)
        return ch
    getch = _getch
except ImportError:
    import msvcrt
    def _getch():
        return msvcrt.getch()
    getch = _getch
