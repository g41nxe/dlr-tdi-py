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
        - delta
        - all

    --file=FILENAME
        .spot and .gathering file must have the same name; exclude file-extension
        for plot use the folder containing multiple spot/gather files

    --type=TYPE (only for plot=delta)
        - position
        - frequency

"""

import getopt, sys, os

from plot import gather, spot, psf, gauss, gauss2d, helper, delta
from common.config import Config
import matplotlib.pyplot as plt


def usage():
    print(__doc__)
    sys.exit(0)


def show(task, file, type=None):

    if not os.path.isabs(file):
        file = Config.PLOT_DATA_FOLDER + file

    if task == 'delta':
        if not os.path.exists(file) or not os.path.isdir(file):
            print("Error: folder " + file + " does not exist!")
            sys.exit(0)

        delta.plot(file, type)
        sys.exit(1)

    for ext in ("spot", "gather"):
        if not os.path.exists(file + "." + ext):
            print("Error: folder " + file + "." + ext + " does not exist!")
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
    elif task == 'gauss2d':
        gauss2d.plot(h, s, g)
    elif task == 'all':
        spot.plot(h, s, g)
        gather.plot(h, s, g)
        psf.plot(h, s, g)
        gauss.plot(h, s, g)

    plt.show()

def main():
    file   = Config.PLOT_DATA_FOLDER + Config.PLOT_DEFAULT_FILE
    action = None
    type   = None

    try:
        opts, args = getopt.getopt(sys.argv[1:], "h", ["help", "plot=", "file=", "type="])

    except getopt.GetoptError as err:
        print("Error: %s", err)
        sys.exit(2)

    for o, a in opts:
        if o in ("-h", "--help"):
            usage()

        elif o in ("--file"):
            file = a

        elif o in ("--type"):
            type = a

        elif o in ("--plot"):
            action = a
        else:
            print("Error: unknown option %s", o)
            sys.exit(2)

    if action is None:
        print("Error: parameter 'plot' is mandatory")
        sys.exit(2)

    show(action, file, type)
    sys.exit(0)


if __name__ == "__main__":
    main()