"""
USAGE:
    python tdi-control [OPTIONS]

OPTIONS:

    -h, --help
        Display this help message.

    --task=FILE
        The file containing config data about the frequency, position, velocity

    --name=NAME
        The (folder-)name of the current run

"""

import getopt
import os
import sys

from common.logger import Logger
from control.clients import *
from control.control import Control

logger = Logger.get_logger()

def usage():
    print(__doc__)


def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "h", ["help", "name=", "task=", "show-config", "reboot"])

    except getopt.GetoptError as err:
        print("Error: ", err)
        sys.exit(2)

    name = None
    tasks = []

    for o, a in opts:
        if o in "--reboot":
            Control.rebootXPS()
            sys.exit()

        if o in "--name":
            name = a

        elif o in "--task":

            if not os.path.isabs(a):
                a = os.path.dirname(os.path.abspath(__file__))+ "\\tasks\\" + a

            for i in a.split(','):
                t = i + '.json'
                if os.path.exists(t):
                    tasks.append(t)
                else:
                    logger.error("Task file %s does'nt exist!", a)

        elif o in "--show-config":
            print(vars(Config))

        else:
            usage()
            sys.exit(2)

    if len(tasks) < 1:
        print("No task!")
        usage()
        sys.exit()

    for t in tasks:
        Control.start(t, name)

if __name__ == "__main__":
    main()
