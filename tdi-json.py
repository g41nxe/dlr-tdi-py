from common.util import *
from common.config import Config

import json

def build_speed_equal_freq_json():
    p = [
        ('CAM_X_GROUP', [259.849]),
        ('CAM_Y_GROUP', [7.1]),
        ('CAM_Z_GROUP', [101.615])
    ]

    runs = {}
    runs['id'] = 'speed-equal-freq'
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
    return json.dumps(runs)


def build_vel_and_freq_range_json():
    p = [
        ('CAM_X_GROUP', [259.849]),
        ('CAM_Y_GROUP', [7.1]),
        ('CAM_Z_GROUP', [101.615])
    ]

    runs = {}
    runs['id'] = 'test-multi-vel'
    runs['runs'] = []

    for v in [81.02, 72.31, 63.87, 55.03]:
        first_freq = True

        for f in get_freq_range_mm(0,60):
            run = {}
            run['param'] = {}

            if first_freq is True:
                run['param']['velocity'] = v

            if (len(runs['runs']) < 1):
                run['param']['position'] = p

            run['param']['frequency'] = f

            runs['runs'].append(run)

            first_freq = False

    return json.dumps(runs)


def build_freq_range_json(v=None):
    if v is None:
        v = Config.get('FP_VELOCITY')

    p = [
            ('CAM_X_GROUP', [259.849] ),
            ('CAM_Y_GROUP', [7.1]),
            ('CAM_Z_GROUP', [101.615])
        ]

    runs = {}
    runs['id'] = 'full-freq-single-velocity'
    runs['runs'] = []

    for f in get_freq_range(255):
        run = {}

        if (len(runs['runs']) < 1):
            run['velocity'] = v
            run['position'] = p

        run['frequency'] = f

        runs['runs'].append(run)

    return json.dumps(runs)

def build_pos_range_json():

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

    return json.dumps(runs)

print(build_speed_equal_freq_json())