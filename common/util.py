import math

import numpy as np


# steps in [0, 255]
def get_freq_range(steps):
    # hard coded values from 9kdemo cam software
    max_freq     = 9615
    sample_count = 1000000
    max          = 256
    min          = 0
    step_range   = max // steps

    if steps > max:
        raise RuntimeError("parameter 'i' cannot be > 256")

    frequencies = []
    for i in range(min, max, step_range):
        delta = int(round(sample_count / max_freq))
        freq  = int(round(sample_count / (delta + i)))

        if freq not in range(2785, 9615+1):
            raise ValueError("frequency '%s' not in range [2786, 9615]", freq)

        frequencies.append(freq)

    return frequencies

# steps in [0, 255]
# freq range [2786, 9615]
def get_freq_range_mm(min, max):
    if max > 255  or min < 0 or min > max:
        raise ValueError

    frequencies = []
    for i in range(min, max, 1):
        freq = bit2freq(i)

        if freq not in range(2785, 9615+1):
            raise ValueError("frequency '%s' not in range [2786, 9615]", freq)

        frequencies.append(freq)

    return frequencies

def get_vel_from_freq(f):
    return f * 0.00875


def fwhm(delta):
    return 2 * math.sqrt(2 * np.log(2)) * abs(delta)

def bit2freq(bit):
    # hard coded values from 9kdemo cam software
    max_freq     = 9615
    sample_count = 1000000

    delta = int(round(sample_count / max_freq))
    freq = int(round(sample_count / (delta + bit)))

    return freq