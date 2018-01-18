import logging
from .util import get_freq_range

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
    FP_START        = -10          # mm
    FP_END          = 10           # mm
    FP_VELOCITY     = 81           # mm/s
    FP_ACCELERATION = 1500         # mm/s^2
    FP_JERKTIME     = [0.02, 0.02] # min, max

    LOG_LEVEL       = logging.INFO

    CLAMP_MAX_INTENSITY = 2500 # intensities > value are outliers
    CLAMP_MIN_INTENSITY = 0    # intensities < value are noise

    PLOT_DATA_FOLDER    = "D:\\Daten\\software\\Python\\dlr-tdi-py\\data\\"
    PLOT_DEFAULT_FILE   = "161117\\rot_Y5to9\\153824_9615hz_position5"

    ITERATIONS = 30

    DEFAULT_FREQUENCY   = "single"

    FREQUENCIES     = {

        "single" : [9615],
        "small"  : get_freq_range(10),
        "full"   : get_freq_range(255),

    }

    DEFAULT_POSITION    = "single"

    POSITIONS       = {

        "single" : [
            [
                (CAM_X_GROUP, [259.849]),
                (CAM_Y_GROUP, [7.1]),
                (CAM_Z_GROUP, [101.615])
            ]
        ]
        ,

        "focus" : [
            [
                (CAM_X_GROUP, [259.849]),
                (CAM_Y_GROUP, [5]),
                (CAM_Z_GROUP, [101.615])
            ],
            [
                (CAM_Y_GROUP, [5.5]),
            ],
            [
                (CAM_Y_GROUP, [6]),
            ],
            [
                (CAM_Y_GROUP, [6.5]),
            ],
            [
                (CAM_Y_GROUP, [7]),
            ],
            [
                (CAM_Y_GROUP, [7.5]),
            ],
            [
                (CAM_Y_GROUP, [8]),
            ],
            [
                (CAM_Y_GROUP, [8.5]),
            ],
            [
                (CAM_Y_GROUP, [9]),
            ]
        ]
    }





