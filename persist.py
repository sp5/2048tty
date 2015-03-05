import os.path
import json

class Persister:
    def __init__(self,
            persistfile=os.getenv("2048TTY_FILE",
                default=os.path.expanduser('~/.2048tty'))):
        self.persistfile = persistfile
        try:
            os.utime(persistfile)
        except:
            open(persistfile, 'a').close()
        with open(persistfile, 'r') as f:
            try:
                self.data = json.load(f)
            except ValueError:
                self.data = {
                    "hiscore": 0,
                }

    def __getitem__(self, item):
        return self.data[item]

    def __setitem__(self, item, value):
        self.data[item] = value
    
    def __delitem__(self, item):
        if item in self.data:
            del self.data[item]

    def __contains__(self, item):
        return item in self.data

    def finish(self):
        with open(self.persistfile, 'w') as f:
            json.dump(self.data, f)
