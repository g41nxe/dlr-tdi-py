"""
USAGE:
    python tdi-control [OPTIONS]

OPTIONS:
    -h, --help
        Display this help message.

    --plot=PLOT
        available PLOTs:
        - gather
        - spot
        - psf
        - gauss

    --file=FILENAME
        .spot and .gathering file must have the same name; exclude file-extension

"""

import getopt, sys, os

from plot import gather, spot, psf, gauss, helper
from common.config import Config


def usage():
    print(__doc__)
    sys.exit(0)


def show(task, file):

    for ext in ("spot", "gather"):
        if not os.path.exists(file + "." + ext):
            print("Error: %s-file does not exist!", ext)
            sys.exit(0)

    h, s = helper.load_spot_file(file + '.spot')
    g    = helper.load_gathering_file(file + '.gather')

    if task == 'spot':
        spot.plot(h, s, g)
    elif task == 'gather':
        gather.plot(h, s, g)
    elif task == 'psf':
        psf.plot(h, s, g)
    elif task == 'gauss':
        gauss.plot(h, s, g)


def main():
    file = os.getcwd() + Config.PLOT_DEFAULT_FILE
    action = None

    try:
        opts, args = getopt.getopt(sys.argv[1:], "hp:f:", ["help", "plot=", "file="])

    except getopt.GetoptError as err:
        print("Error: %s", err)
        sys.exit(2)

    for o, a in opts:
        if o in ("-h", "--help"):
            usage()

        elif o in ("-f", "--file"):
            file = a

        elif o in ("-p", "--plot"):
            action = a
        else:
            print("Error: unknown option %s", o)
            sys.exit(2)

    if action is None:
        print("Error: parameter 'plot' is mandatory")
        sys.exit(2)

    show(action, file)
    sys.exit(0)


if __name__ == "__main__":
    main()