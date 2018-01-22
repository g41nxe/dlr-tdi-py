
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
def get_freq_range_mm(min, max):
    # hard coded values from 9kdemo cam software
    max_freq     = 9615
    sample_count = 1000000

    if max > 255  or min < 0 or min > max:
        raise ValueError

    frequencies = []
    for i in range(min, max, 1):
        delta = int(round(sample_count / max_freq))
        freq  = int(round(sample_count / (delta + i)))

        if freq not in range(2785, 9615+1):
            raise ValueError("frequency '%s' not in range [2786, 9615]", freq)

        frequencies.append(freq)

    return frequencies