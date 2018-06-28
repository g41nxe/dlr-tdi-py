import getopt
import json
import os
import re
import sys

import numpy as np
from common.config import Config
from common.data import *
from common.logger import Logger
from common.util import *


def json_repair(folder):
    spot_size = 6000 * 1024  # KB
    gather_size = 1000 * 1024  # KB

    if not os.path.isabs(folder):
        folder = Config.get("PLOT_DATA_FOLDER") + folder

    if not os.path.exists(folder) or not os.path.isdir(folder):
        print("Error: folder " + folder + " does not exist!")
        sys.exit(0)

    errors = {}
    for root, dirs, files in os.walk(folder):
        for file in files:
            if not file.endswith('.spot') and not file.endswith('.gather'):
                continue

            if (file.endswith('.spot') and os.path.getsize(folder + '/' + file) < spot_size) or \
                    (file.endswith('.gather') and os.path.getsize(folder + '/' + file) < gather_size):
                Logger.get_logger().debug('File to small: ' + file)

                name, ext = os.path.splitext(file)
                pattern = r"(\d*)_([\d\w-]*)_(\d*)"
                m = re.search(pattern, name)

                errors[name] = ((m.group(1), m.group(2), m.group(3)))

    runs_by_task = loadRuns()

    runs = {}
    runs['id'] = 'repair'
    runs['desc'] = 'Repeat previously broken runs'

    runs['runs'] = []

    for name in errors:
        (id, task, run_id) = errors[name]

        old_run = runs_by_task[task][int(run_id)]

        run = {}
        run['velocity'] = old_run.vel
        run['position'] = old_run.pos
        run['frequency'] = old_run.freq
        run['config'] = old_run.cfg

        runs['runs'].append(run)

        print(run)

    return runs


def json_mtf():
    p = [
        ('CAM_X_GROUP', [259.849]),
        ('CAM_Y_GROUP', [7.1]),
        ('CAM_Z_GROUP', [101.615])
    ]

    runs = {}
    runs['id'] = 'regular'
    runs['desc'] = 'Messablauf mit synchronen FPS + TDI Geschwindigkeiten zur Erzeugung von PSF und MTF Kurven'

    runs['runs'] = []

    for f in get_freq_range_mm(0, 60):

        v = get_vel_from_freq(f)
        run = {}

        if (len(runs['runs']) < 1):
            run['position'] = p

        run['frequency'] = f
        run['velocity'] = v
        run['cfg'] = {'ITERATIONS': 5}

        runs['runs'].append(run)

    return runs

def json_speedratio(f):
    p = [
        ('CAM_X_GROUP', [259.849]),
        ('CAM_Y_GROUP', [7.1]),
        ('CAM_Z_GROUP', [101.615])
    ]

    steps = 3
    start = round(get_vel_from_freq(f) * 0.6, 4)
    stop = round(get_vel_from_freq(f) * 1.4, 4)
    iterations = 30

    runs = {}
    runs['id'] = 'speed-ratio-f' + str(f) + 's' + str(steps) + 'i' + str(iterations)
    runs['desc'] = 'Speed-Ratio Messung mit fester Frequenz von ' + str(f) + \
                   'hz und dynamischer Geschwindigkeit zwischen [ ' + str(start) + ', ' + str(stop) + ' ]'

    runs['runs'] = []

    for v in np.linspace(start, stop, steps):
        run = {}
        run['velocity'] = round(v, 4)
        run['position'] = p
        run['frequency'] = f
        run['config'] = [("ITERATIONS", iterations)]

        runs['runs'].append(run)

    return runs

def json_focus():
    y = 5.0

    p = [
        ('CAM_X_GROUP', [259.849]),
        ('CAM_Y_GROUP', [y]),
        ('CAM_Z_GROUP', [101.615])
    ]

    runs = {}
    runs['id'] = 'focus'
    runs['desc'] = 'Iteration entlang der Y-Achse zur Fokus-Kalibrierung'
    runs['runs'] = []

    for f in range(0, 9):
        run = {}

        if (len(runs['runs']) < 1):
            run['velocity'] = Config.get('FP_VELOCITY')
            run['frequency'] = 9615
            run['position'] = p

        run['position'] = [
            ('CAM_Y_GROUP', [y]),
        ]

        runs['runs'].append(run)
        y += .5

    return runs


def json_test():
    p = [
        ('CAM_X_GROUP', [259.849]),
        ('CAM_Y_GROUP', [7.1]),
        ('CAM_Z_GROUP', [101.615])
    ]

    runs = {}
    runs['id'] = 'test'
    runs['desc'] = 'Test-Messung'
    runs['runs'] = []

    run = {}
    run['velocity'] = Config.get('FP_VELOCITY')
    run['frequency'] = 9615
    run['position'] = p

    runs['runs'].append(run)

    return runs

def writeTask(runs):
    fname = os.path.dirname(os.path.abspath(__file__)) + "\\tasks\\" + str(runs['id'])

    Logger.get_logger().info('Writing JSON file %s', str(runs['id']))
    with open(fname + '.json', 'w') as outfile:
        json.dump(runs, outfile)

def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], "", ["test", "focus", "speed-ratio", "equal", "repair="])

    except getopt.GetoptError as err:
        print("Error: ", err)
        sys.exit(2)

    data = []

    for o, a in opts:
        if o in ("--focus"):
            data.append(json_focus())

        elif o in ("--speed-ratio"):
            for f in [9259, 6211, 2817]:
                data.append(json_speedratio(f))

        elif o in ("--equal"):
            data.append(json_mtf())

        elif o in ("--repair"):
            data.append(json_repair(a))

        elif o in ("--test"):
            data.append(json_test())

    for task in data:
        writeTask(task)


if __name__ == "__main__":
    main()
