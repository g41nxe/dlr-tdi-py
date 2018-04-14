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
        - movie

    --file=FILENAME
        .spot and .gathering file must have the same name; exclude file-extension
        for plot use the folder containing multiple spot/gather files

    --save (speedratio + movie)

"""

import getopt, sys, os
import matplotlib.pyplot as plt

from common.data import *
from plot.graph import gather, psf, gauss, speedratio, spot, mtf
from plot.animation import spot as movie

from common.config import Config

def usage():
    print(__doc__)
    sys.exit(0)


def show(task, file, type=None, save=False):

    if not os.path.isabs(file):
        file = Config.get("PLOT_DATA_FOLDER") + file


    if task == 'speedratio':
        if not os.path.exists(file) or not os.path.isdir(file):
            print("Error: folder " + file + " does not exist!")
            sys.exit(0)

        speedratio.plot(file, save)
        sys.exit(1)

    if task == 'movie':
        if not os.path.exists(file) or not os.path.isdir(file):
            print("Error: folder " + file + " does not exist!")
            sys.exit(0)

        movie.plot(file, save)
        sys.exit(1)

    for ext in ("spot", "gather"):
        if not os.path.exists(file + "." + ext):
            print("Error: folder " + file + "." + ext + " does not exist!")
            sys.exit(0)

    h, s = loadSpotFile(file + '.spot')
    g    = loadGatheringFile(file + '.gather')

    if task == 'spot':
        spot.plot(h, s, g)

    elif task == 'gather':
        gather.plot(h, s, g)

    elif task == 'psf':
        psf.plot(h, s, g)

    elif task == 'gauss':
        gauss.plot(h, s, g)

    elif task == 'mtf':
        mtf.plot(h, s, g)

    plt.show()

def main():
    file   = Config.get("PLOT_DATA_FOLDER") + Config.get("PLOT_DEFAULT_FILE")
    action = None
    type   = None
    save   = False

    try:
        opts, args = getopt.getopt(sys.argv[1:], "h", ["help", "plot=", "file=", "type=", "save"])

    except getopt.GetoptError as err:
        print("Error: %s", err)
        sys.exit(2)

    for o, a in opts:
        if o in ("-h", "--help"):
            usage()

        elif o in ("--save"):
            save = True

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

    show(action, file, type, save)
    sys.exit(0)


if __name__ == "__main__":
    main()