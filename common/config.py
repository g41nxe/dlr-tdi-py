import logging, sys


def save_to_file(folder, id):
    file = folder + "\\" + id + "_versuchsdaten.txt"

    f = open(file, "w")

    for name in dir(Config):
        if callable(getattr(Config, name)) or name.startswith("__"):
            break

        value = getattr(Config, name)

        f.write(str(name) + ": " + str(value) + "\n")

    f.close()

# i in [0, 255]
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

class Config:

    CAM_HOST         = "192.168.0.77"
    CAM_PORT         = 8089
    CAM_X_GROUP      = "GROUP2"
    CAM_Y_GROUP      = "GROUP5"
    CAM_Z_GROUP      = "GROUP4"
    CAM_RESULT_PATH  = "G:\\data\\messdaten"
    CAM_PROGRAM_PATH = "G:\\Projekte\\01_9kDEMO\\SOFTWARE\\Kari\\TDI_9k\\TDI_9k_Demo_100429.exe"

    XPS_HOST        = "192.168.0.254"
    XPS_PORT        = 5001
    XPS_FTP_PATH    = "public"
    XPS_FTP_FILE    = "Gathering.dat"
    XPS_USER        = "Administrator"
    XPS_PASSWORD    = "Administrator"
    XPS_RESULT_PATH = "T:\\messdaten"
    XPS_TRIGGER     = "GPIO1.DI.DILowHigh"
    XPS_DATA_TYPES  = ["CurrentPosition", "CurrentVelocity"]

    FP_GROUP        = "GROUP3"
    FP_GROUP_NAME   = "POSITIONER"
    FP_START        = -10   # mm
    FP_END          = 10    # mm
    FP_VELOCITY     = 81    # mm/s
    FP_ACCELERATION = 1500  # mm/s^2
    FP_JERKTIME     = [0.02, 0.02] # min, max

    # The following should be adjustable later on

    LOG_LEVEL       = logging.DEBUG

    ITERATIONS      = 30                      # number of iterations
    FREQUENCIES     = get_freq_range(10)      # for each frequency
    POSITIONS = (                             # for all this positions
        [
            (CAM_X_GROUP, [259.849]),
            (CAM_Y_GROUP, [7]),
            (CAM_Z_GROUP, [101.615])
        ],
    )

    CLAMP_MAX_INTENSITY = 1000  # intensities > value are outliers
    CLAMP_MIN_INTENSITY = 100   # intensities < value are noise

    PLOT_DEFAULT_FILE = "\\data\\161117\\rot_Y5to9\\153824_9615hz_position6"

    __logger = None

    @staticmethod
    def get_logger():

        if not Config.__logger is None:
            return Config.__logger

        formatter = logging.Formatter("%(asctime)s - %(message)s")

        ch = logging.StreamHandler(sys.stdout)
        ch.setLevel(Config.LOG_LEVEL)
        ch.setFormatter(formatter)

        logger = logging.getLogger("global")
        logger.setLevel(Config.LOG_LEVEL)
        logger.addHandler(ch)

        Config.__logger = logger

        return logger


