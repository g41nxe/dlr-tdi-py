from datetime import datetime
from .config import Config

import logging, sys, re, os
import numpy as np

logger = logging.getLogger(__name__)
logger.setLevel(Config.LOG_LEVEL)
ch = logging.StreamHandler(sys.stdout)
ch.setLevel(Config.LOG_LEVEL)
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
ch.setFormatter(formatter)
logger.addHandler(ch)

# i in [0, 255]
def get_freq(i):

    # hard coded values from 9kdemo cam software
    max_freq = 9615
    steps    = 1000000

    delta = int(round(steps / max_freq))
    freq  = int(round(steps / (delta + i)))

    if freq not in range(2786, 9615+1):
        logger.error("frequency '%s' not in range [2786, 9615]", freq)
        raise Exception

    return freq

def load_spot_file(spot_file):

    if not os.path.exists(spot_file):
        raise ValueError("File %s does not exist!")

    header = dict()

    with open(spot_file, "r") as fp:
        for line in fp:
            m = re.search("\[([aA-zZ -]+)\]([0-9.:]+)", line)

            if m is None:
                break

            header[m.group(1)] = m.group(2)

    header['FirstPixel'] = int(header['FirstPixel'])
    header['LastPixel'] = int(header['LastPixel'])
    header['NrReadOuts'] = int(header['NrReadOuts'])
    header['TDI-Stages'] = int(header['TDI-Stages'])
    header['LineFreq'] = float(header['LineFreq'])
    header['Date'] = datetime.strptime(header['Date'], '%d.%m.%Y')
    header['Time'] = datetime.strptime(header['Time'], '%H:%M:%S')
    header['PixelCount'] = header['LastPixel'] - header['FirstPixel'] + 1
    header['LineCount'] = header['NrReadOuts']

    z = np.reshape(np.fromfile(spot_file, dtype=np.ushort)[:-8 * header['PixelCount']],
                   (header['LineCount'], header['PixelCount']))

    return header, z

def load_gathering_file(gathering_file):
    if not os.path.exists(gathering_file):
        raise ValueError("File %s does not exist!")

    return np.loadtxt(gathering_file, skiprows=2)

def align_data(spot_data, gathering_data):
    pass
