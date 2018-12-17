import os
from time import sleep

module = ""

for f in sorted(os.listdir()):
    if f in ['main.py', 'boot.py', 'config.py']:
        continue

    try:
        print("starting module %s" % f)
        m = __import__(f[:-3])
        m.setup()
        while True:
            m.loop()

    except ImportError as err:
        print("Cannot import module %s.\n%s\nTrying the next one..." % (f, err))


print("No files other than main.py and boot.py found. Can't do shit, sorry!")
while True:
    sleep(100)

