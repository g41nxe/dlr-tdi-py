import io
import os
import re
import csv

from pathlib import Path
from abc import ABCMeta, abstractmethod
from datetime import datetime

import numpy as np

from common.peaks  import detect_peaks
from common.config import Config
from common.logger import Logger
from control.run   import RunConfig


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
    data = np.genfromtxt(gathering_file, skip_header=2)

    if len(data) < 1:
        Logger.get_logger().warning("spot file " + gathering_file + " is empty")

    return data


def extractBrightestSpots(header, spot, gather):
    x, y = buildCorrectedData(header, spot, gather)

    line, col = np.unravel_index(y.argmax(), y.shape)
    tops = detect_peaks(y[:, col], mph=y[:,col].max() * 0.75, mpd=200, edge='rising')
    pixelCount = header["PixelCount"]

    ydata = []
    for line in tops:
        start_row = np.maximum(line - int(round(pixelCount / 2)), 0)
        end_row = np.minimum(line + int(round(pixelCount / 2)), (len(y) - 1))

        ydata.append(y[start_row:end_row, :])

    return ydata, col

def extractBrightestSpot(header, spot, gather):
    x, y = buildCorrectedData(header, spot, gather)

    pixelCount = header["PixelCount"]

    line, col = np.unravel_index(y.argmax(), y.shape)

    start_row = np.maximum(line - int(round(pixelCount / 2)), 0)
    end_row   = np.minimum(line + int(round(pixelCount / 2)), (len(y) - 1))

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

    value      = data[int_index_aligned]
    next_value = data[int_next_index_aligned]

    value += ((index_aligned - int_index_aligned) * (next_value - value))

    return value


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

class NPYLoader():
    __metaclass__ = ABCMeta

    def __init__(self, subdirectory):
        self.subdirectory = subdirectory

    @abstractmethod
    def buildAndAppendData(id, header, spot, gather, run, data):
        pass

    def loadNPY(self):
        data = {}

        for item in os.listdir(self.subdirectory):
            if not os.path.isfile(os.path.join(self.subdirectory, item)):
                continue

            if not item.endswith('.npy'):
                continue

            name, ext = os.path.splitext(item)
            data[name] = np.load(os.path.join(self.subdirectory, item), encoding='latin1')

        return data

    def saveNPY(self):

        data = {}
        runs = loadRuns()

        for root, dirs, files in os.walk(self.subdirectory):
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
                    data = self.buildAndAppendData(id, header, spot, gather, run, data)
                except Exception as e:
                    print(e)
                    continue

        for id in data.keys():
            f = self.subdirectory + "\\" + id
            np.save(f, data[id])

        return data

    @staticmethod
    def generateCSVs(data):
        list_len = len(data)
        if not list_len:
            raise ValueError()

        csv_folder = Path(Config.get('PLOT_DATA_FOLDER')) / 'csv'
        if not csv_folder.exists():
            csv_folder.mkdir()

        for id, array in data.items():
            NPYLoader.writeCSV(array.tolist(), csv_folder / f'{id}.csv')

    @staticmethod
    def writeCSV(data, csv_file):
        types = list(set(data.keys()).difference(('pixel',)))
        data_len = len(data[types[0]])
        Logger.get_logger().info("Writing csv file " + csv_file)
        
        with open(csv_file, 'w') as fh:
            f = csv.writer(fh)
            f.writerow(types)

            for data_pos in range(data_len):
                data_row = []
                for type_ in types:
                    data_row.append(round(data[type_][data_pos], 6))
                f.writerow(data_row)
