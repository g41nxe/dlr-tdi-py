"""
USAGE:
    python -m control.client [OPTIONS]

OPTIONS:
    -h, --help
        Display this help message.
    --start
        Start the Server for 9kdemo camera software
"""

from camera.server import *

import getopt

def usage():
    print(__doc__)

def start():
    s = Server()
    s.start()

def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "h", ["help", "start"])

    except getopt.GetoptError as err:
        print("Error: %s", err)
        usage()
        sys.exit(2)

    for o, a in opts:
        if o in ["--help", "h"]:
            usage()
            sys.exit(2)

    start()

if __name__ == "__main__":
    main()

