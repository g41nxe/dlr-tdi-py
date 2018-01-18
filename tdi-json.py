from common.util import *
from common.config import Config

import json

def build_vel_and_freq_range_json():
    p = [
        ('CAM_X_GROUP', [259.849]),
        ('CAM_Y_GROUP', [7.1]),
        ('CAM_Z_GROUP', [101.615])
    ]

    runs = {}
    runs['id'] = 'full-freq-3-velocities'
    runs['runs'] = []

    for v in [81, 55, 22]:
        first_freq = True

        for f in get_freq_range(255):
            run = {}

            if first_freq is True:
                run['velocity'] = v

            if (len(runs['runs']) < 1):
                run['position'] = p

            run['frequency'] = f

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

print(build_freq_range_json())
print(build_pos_range_json())
print(build_vel_and_freq_range_json())