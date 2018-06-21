"""
USAGE:
    python -m control.client [OPTIONS]

OPTIONS:
    -h, --help
        Display this help message.
    --start
        Start the Server for 9kdemo camera software
"""

from camera.cameraserver import CameraServer
from camera.neunkdemo import Neunkdemo

import getopt, sys, time

def test():
    program = Neunkdemo()
    program.set_frequency(6666)
    time.sleep(2)
    program.profile_start()
    time.sleep(10)
    program.stop_store_sector("test")
    time.sleep(2)
    program.profile_stop()

def usage():
    print(__doc__)

def start():
    s = CameraServer()
    s.start()

def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "h", ["help", "start", "test"])

    except getopt.GetoptError as err:
        print("Error: %s", err)
        usage()
        sys.exit(2)

    for o, a in opts:
        if o in ["--help", "h"]:
            usage()
            sys.exit(2)

        if o in ["--test"]:
            test()
            sys.exit(2)

    start()

if __name__ == "__main__":
    main()

