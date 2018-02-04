from datetime import datetime
from common.config import Config
from common.logger import Logger

import re, io
import numpy as np

def load_spot_file(spot_file):
    header = dict()

    with io.open(spot_file, "r", encoding="ISO-8859-1") as fp:
        for line in fp:
            m = re.search(r"\[([aA-zZ -]+)\]([0-9.:]+)", line)

            if m is None:
                break

            header[m.group(1)] = m.group(2)

    header['FirstPixel'] = int(header['FirstPixel'])
    header['LastPixel']  = int(header['LastPixel'])
    header['NrReadOuts'] = int(header['NrReadOuts'])
    header['TDI-Stages'] = int(header['TDI-Stages'])
    header['LineFreq']   = float(header['LineFreq'])
    header['Date']       = datetime.strptime(header['Date'], '%d.%m.%Y')
    header['Time']       = datetime.strptime(header['Time'], '%H:%M:%S')
    header['PixelCount'] = header['LastPixel'] - header['FirstPixel'] + 1
    header['LineCount']  = header['NrReadOuts']
    header['PixelSize']  = 0.00875 # milimeter

    z = np.reshape(np.fromfile(spot_file, dtype=np.ushort)[:-8 * header['PixelCount']],
                   (header['LineCount'], header['PixelCount']))

    if (len(z) < 1):
        Logger.get_logger().warning("spot file " + spot_file + " is empty")

    return header, z

def load_gathering_file(gathering_file):
    data = np.loadtxt(gathering_file, skiprows=2)

    if len(data) < 1:
        Logger.get_logger().warning("spot file " + gathering_file + " is empty")

    return data

def align_data(header, spot_data, gathering_data):
    position = gathering_data[:, 0]
    speed    = gathering_data[:, 1]

    alpha       = (10000 / header['LineFreq'])
    aligned_size = min(int((len(position) / alpha)), len(spot_data))
    spot_data    = spot_data[1:aligned_size, :]

    # temporary storage for data lines
    valid_lines = []

    # calculate valid lines and values
    x = []
    y = []

    for line in range(0, len(spot_data)):
        # position doesn't exist
        try :
            current_position = get_aligned_data(line, alpha, position)
            current_speed    = get_aligned_data(line, alpha, speed)
        except IndexError:
            break

        # only store data in radius of pixelCount pixels
        # remove outlier and backwards travel
        if Config.get('FP_START') <= current_position and Config.get('FP_END') >= current_position \
            and current_speed > 0 \
            and np.min(spot_data[line, :]) <  Config.get('CLAMP_MAX_INTENSITY') \
            and np.max(spot_data[line, :]) >= Config.get('CLAMP_MIN_INTENSITY'):


            x.append(current_position)
            y.append(spot_data[line, :])

    return np.array(x), np.array(y)

# fix errors due to different recording frequencies of 9kdemo and xps
def get_aligned_data(index, alpha, data):
    index_aligned      = index * alpha
    next_index_aligned = (index + 1) * alpha

    int_index_aligned      = int(round(index_aligned))
    int_next_index_aligned = int(round(next_index_aligned))

    value = data[int_index_aligned]
    next_value = data[int_next_index_aligned]

    value += ((index_aligned - int_index_aligned) * (next_value - value))

    return value
