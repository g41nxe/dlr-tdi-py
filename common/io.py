from datetime import datetime
from common.config import Config
from common.logger import Logger
from control.run import Run, RunConfig

import re, io, os
import numpy as np

def loadSpotFile(spot_file):
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

def loadGatheringFile(gathering_file):
    data = np.loadtxt(gathering_file, skiprows=2)

    if len(data) < 1:
        Logger.get_logger().warning("spot file " + gathering_file + " is empty")

    return data

def extractBrightestSpot(header, spot, gather):
    x, y = buildCorrectedData(header, spot, gather)

    pixelCount = header["PixelCount"]

    line, col = np.unravel_index(y.argmax(), y.shape)
    start_row = np.maximum(line - int(round(pixelCount / 2)), 0)
    end_row = np.minimum(line + int(round(pixelCount / 2)), (len(y) - 1))
    ydata = y[start_row:end_row, :]

    return ydata

def buildCorrectedData(header, spot_data, gathering_data):
    position = gathering_data[:, 0]
    speed    = gathering_data[:, 1]

    alpha        = (10000 / header['LineFreq']) # factor to fix frequency difference between xps and tdi cam
    aligned_size = min(int((len(position) / alpha)), len(spot_data))
    spot_data    = spot_data[1:aligned_size, :]

    # calculate valid lines and values
    x = []
    y = []

    for line in range(0, len(spot_data)):
        # position doesn't exist
        try :
            current_position = getFrequencyAlignedData(line, alpha, position)
            current_speed    = getFrequencyAlignedData(line, alpha, speed)
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
def getFrequencyAlignedData(index, alpha, data):
    index_aligned      = index * alpha
    next_index_aligned = (index + 1) * alpha

    int_index_aligned      = int(round(index_aligned))
    int_next_index_aligned = int(round(next_index_aligned))

    value = data[int_index_aligned]
    next_value = data[int_next_index_aligned]

    value += ((index_aligned - int_index_aligned) * (next_value - value))

    return value

def loadNPY(subdirectory):
    data = {}

    for item in os.listdir(subdirectory):
        if not os.path.isfile(os.path.join(subdirectory, item)):
            continue

        if not item.endswith('.npy'):
            continue

        name, ext = os.path.splitext(item)
        data[name] = np.load(os.path.join(subdirectory, item))

    return data

def loadRuns():
    runs = {}

    for root, dirs, files in os.walk(os.path.dirname(os.path.abspath(__file__)) + "\\..\\tasks\\" ):
        for file in files:
            name, ext = os.path.splitext(file)
            if not (name + ".json") in files:
                continue

            Logger.get_logger().info("Loading task %s", name)
            taskfile = os.path.join(root, name) + '.json'
            cfg = RunConfig(taskfile)
            runs[name] = {}
            runs[name] = cfg.getRuns()

    return runs

def saveNPY(subdirectory, func):

    data = {}
    runs = loadRuns()

    for root, dirs, files in os.walk(subdirectory):
        for file in files:
            if (not file.endswith('.spot')):
                continue

            name, ext = os.path.splitext(file)
            if not (name + ".gather") in files:
                continue

            pattern = r"(\d*)_([\d\w-]*)_(\d*)"
            m = re.search(pattern, name)

            if m is None:
                continue

            id      = m.group(1)
            task    = m.group(2)
            run_id  = m.group(3)

            Logger.get_logger().info("Loading %s", name)

            if not task in runs.keys():
                Logger.get_logger().warn("Task %s not found", task)

            header, spot = loadSpotFile(os.path.join(root, name) + '.spot')
            gather       = loadGatheringFile(os.path.join(root, name) + '.gather')
            run          = runs[task][int(run_id)]

            try:
                data = func(id, header, spot, gather, run, data)
            except Exception as e:
                print(e)
                continue

    for id in data.keys():
        f = subdirectory + "\\" + id
        np.save(f, data[id])

    return data