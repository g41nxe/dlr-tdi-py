from common.util import *
from common.config import Config
from common.logger import Logger
import os, getopt, sys

import json

def json_equal():
    p = [
        ('CAM_X_GROUP', [259.849]),
        ('CAM_Y_GROUP', [7.1]),
        ('CAM_Z_GROUP', [101.615])
    ]

    runs = {}
    runs['id'] = 'equal'
    runs['runs'] = []


    for f in get_freq_range_mm(0, 60):

        v = get_vel_from_freq(f)
        run = {}
        run['param'] = {}

        if (len(runs['runs']) < 1):
            run['param']['position'] = p

        run['param']['frequency'] = f
        run['param']['velocity']  = v

        runs['runs'].append(run)

    return runs

def json_speed(v):
    p = [
        ('CAM_X_GROUP', [259.849]),
        ('CAM_Y_GROUP', [7.1]),
        ('CAM_Z_GROUP', [101.615])
    ]

    runs = {}
    runs['id'] = 'speed-' + str(round(v))
    runs['runs'] = []

    for f in get_freq_range_mm(0,60): #60):
        run = {}
        run['param'] = {}
        run['param']['velocity']  = v
        run['param']['position']  = p
        run['param']['frequency'] = f

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
    runs['runs'] = []

    for f in range(0,9):
        run = {}

        if (len(runs['runs']) < 1):
            run['velocity']  = Config.get('FP_VELOCITY')
            run['frequency'] = 9615
            run['position']  = p

        run['position'] = [
            ('CAM_Y_GROUP', [y]),
        ]

        runs['runs'].append(run)
        y += .5

    return runs

def writeTask(runs):
    fname = os.path.dirname(os.path.abspath(__file__)) + "\\tasks\\" + str(runs['id'])

    Logger.get_logger().info('Writing JSON file %s', str(runs['id']))
    with open(fname + '.json', 'w') as outfile:
        json.dump(runs, outfile)

def main():

    try:
        opts, args = getopt.getopt(sys.argv[1:], "", ["focus", "speed", "equal"])

    except getopt.GetoptError as err:
        print("Error: ", err)
        sys.exit(2)

    data = []

    for o, a in opts:
        if o in ("--focus"):
            data.append(json_focus())

        elif o in ("--speed"):
            for v in [81.02, 63.87, 55.03]:
                data.append(json_speed(v))

        elif o in ("--equal"):
            data.append(json_equal())

    for task in data:
        writeTask(task)

if __name__ == "__main__":
    main()
