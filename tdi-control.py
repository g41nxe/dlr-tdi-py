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

from common.logger import Logger
from control.clients import *
from control.control import Control
from control.run import RunConfig, Run

from threading import Thread
import getopt, sys, time, os

logger = Logger.get_logger()

def usage():
    print(__doc__)


def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "h", ["help", "name=", "task=", "show-config"])

    except getopt.GetoptError as err:
        print("Error: ", err)
        sys.exit(2)

    name = task = None

    for o, a in opts:

        if o in "--name":
            name = a

        elif o in "--task":
            a += ".json"

            if not os.path.isabs(a):
                a = os.path.dirname(os.path.abspath(__file__))+ "\\tasks\\" + a

            if os.path.exists(a):
                task = a
            else:
                print("Task file %s does'nt exist!", a)

        elif o in "--show-config":
            print(vars(Config))

        else:
            usage()
            sys.exit(2)

    if task is None:
        print("No task!")
        usage()
        sys.exit()

    Control.start(task, name)

if __name__ == "__main__":
    main()
