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
    header['PixelSize'] = 0.00875 #milimeter

    z = np.reshape(np.fromfile(spot_file, dtype=np.ushort)[:-8 * header['PixelCount']],
                   (header['LineCount'], header['PixelCount']))

    return header, z

def load_gathering_file(gathering_file):
    if not os.path.exists(gathering_file):
        raise ValueError("File %s does not exist!", gathering_file)

    return np.loadtxt(gathering_file, skiprows=2)

def align_data(header, spot_data, gathering_data):
    position = gathering_data[:, 0]
    speed    = gathering_data[:, 1]
    pixel    = int(round(header['PixelCount'] / 2))
    clock    = (10000 / header['LineFreq'])
    lines    = []
    j        = 0

    for i in range(0, header['LineCount']):
        position_index = int(round(i * clock))

        # position doesn't exist
        try :
            current_position = get_data(i, clock, position)
            current_speed    = get_data(i, clock, speed)
        except IndexError:
            break

        # only store data in radius of pixelCount pixels
        # remove outlier and backwards travel
        if abs(current_position) < 1 and spot_data[i, pixel] < Config.CLAMP_INTENSITY and current_speed > 0:
            lines.append([j, i, current_position])
            j +=1

    x = np.empty(len(lines))
    y = np.empty([len(lines), header['PixelCount']])

    for j, i, current_position in lines:
        x[j] = current_position
        y[j, :] = spot_data[i, :]

    return x, y

# fix errors due to different recording frequencies of 9kdemo and xps
def get_data(index, clock, data):
    position_index = index * clock

    position_index_rounded = int(round(index * clock))
    next_position_rounded = int(round((index + 1) * clock))

    position = data[position_index_rounded]
    next_position = data[next_position_rounded]

    position += ((position_index - position_index_rounded) * (next_position - position))

    return position
