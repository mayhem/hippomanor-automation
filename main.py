import os
from time import sleep

for f in sorted(os.listdir()):
    if f in ['main.py', 'boot.py', '_config.py', 'net_config.py']:
        continue

    try:
        if f.startswith("config"):
            config = __import__(f[:-3])
        else:
            continue

        with open(f, "rb") as rh:
            with open("_config.py", "w") as wh:
                wh.write(rh.read())

    except ImportError as err:
        print("Cannot import config module %s.\n%s\nTrying the next one..." % (f, err))
        continue

    try:
        print("starting module %s" % config.SCRIPT)
        m = __import__(config.SCRIPT)
        m.setup()
        while True:
            m.loop()

    except ImportError as err:
        print("Cannot import module %s.\n%s\nTrying the next one..." % (f, err))


print("No files other than main.py and boot.py found. Can't do shit, sorry!")
while True:
    sleep(100)

