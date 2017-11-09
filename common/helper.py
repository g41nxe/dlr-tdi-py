from datetime import datetime
from .config import Config

import re, os
import numpy as np

# i in [0, 255]
def get_freq(i):

    # hard coded values from 9kdemo cam software
    max_freq = 9615
    steps    = 1000000

    delta = int(round(steps / max_freq))
    freq  = int(round(steps / (delta + i)))

    if freq not in range(2786, 9615+1):
        raise ValueError("frequency '%s' not in range [2786, 9615]", freq)

    return freq

def load_spot_file(spot_file):
    header = dict()

    with open(spot_file, "r") as fp:
        for line in fp:
            m = re.search("\[([aA-zZ -]+)\]([0-9.:]+)", line)

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

    return header, z

def load_gathering_file(gathering_file):
    return np.loadtxt(gathering_file, skiprows=2)

def align_data(header, spot_data, gathering_data):
    position = gathering_data[:, 0]
    speed    = gathering_data[:, 1]

    pixel       = int(round(header['PixelCount'] / 2))
    alpha       = (10000 / header['LineFreq'])

    aligned_size = min(int((len(position) / alpha)), len(spot_data))
    spot_data    = spot_data[1:aligned_size, :]

    # temporary storage for data lines
    valid_lines = []

    # calculate valid lines and values
    j = 0
    for line in range(0, len(spot_data)):
        # position doesn't exist
        try :
            current_position = get_aligned_data(line, alpha, position)
            current_speed    = get_aligned_data(line, alpha, speed)
        except IndexError:
            break

        # only store data in radius of pixelCount pixels
        # remove outlier and backwards travel
        if Config.FP_START <= current_position and Config.FP_END >= current_position\
            and spot_data[line, pixel] < Config.CLAMP_INTENSITY \
            and current_speed > 0:

            valid_lines.append([j, line, current_position])
            j +=1

    # init arrays
    x = np.empty(len(valid_lines)) # position
    y = np.empty([len(valid_lines), header['PixelCount']]) # intensity

    # build data arrays
    for j, line, current_position in valid_lines:
        x[j] = current_position
        y[j, :] = spot_data[line, :]

    return x, y

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
