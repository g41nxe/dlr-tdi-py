"""
USAGE:
    python tdi-control [OPTIONS]

OPTIONS:
    -h, --help
        Display this help message.
    --show=PLOT
        available PLOTs:
        - gather
        - spot
        - psf

"""

import getopt, sys, os

from view import gather, spot, psf
from common import helper

def usage():
    print(__doc__)

def show(task):

    #file = "D:\\Daten\\1707\\weiss-15um-1"
    file = os.getcwd() + '\\data\\021117\\160128_2786hz'
    h, s = helper.load_spot_file(file + '.spot')
    g    = helper.load_gathering_file(file + '.gather')
    
    if task == 'spot':
        spot.plot(h, s, g)
    if task == 'gather':
        gather.plot(h, s, g)
    if task =='psf':
        psf.plot(h, s, g)

def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "h", ["help", "show="])

    except getopt.GetoptError as err:
        print("Error: %s", err)
        usage()
        sys.exit(2)

    for o, a in opts:
        if o in "--show":
            show(a)

if __name__ == "__main__":
    main()
