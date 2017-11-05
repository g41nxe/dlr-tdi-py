import logging

class Config:

    CAM_HOST         = '192.168.0.77'
    CAM_PORT         = 8089
    CAM_X_GROUP      = 'GROUP2'
    CAM_Y_GROUP      = 'GROUP5'
    CAM_Z_GROUP      = 'GROUP4'
    CAM_RESULT_PATH  = "G:\\data\\messdaten"
    CAM_PROGRAM_PATH = "G:\\Projekte\\01_9kDEMO\\SOFTWARE\\Kari\\TDI_9k\\TDI_9k_Demo_100429.exe"

    XPS_HOST        = '192.168.0.254'
    XPS_PORT        = 5001
    XPS_FTP_PATH    = 'public'
    XPS_FTP_FILE    = 'Gathering.dat'
    XPS_USER        = 'Administrator'
    XPS_PASSWORD    = 'Administrator'
    XPS_RESULT_PATH = "T:\\messdaten"
    XPS_TRIGGER     = "GPIO1.DI.DILowHigh"
    XPS_DATA_TYPES  = ["CurrentPosition", "CurrentVelocity"]

    FP_START        = -10
    FP_END          = 10
    FP_ITERATIONS   = 30
    FP_GROUP        = 'GROUP3'
    FP_GROUP_NAME   = 'POSITIONER'

    # The following should be adjustable later on

    CLAMP_INTENSITY = 5000

    LOG_LEVEL       = logging.DEBUG

    FREQUENCIES     = [2786, 9615]

    POSITIONS       = (
        (
            (CAM_X_GROUP, [259.849]),
            (CAM_Y_GROUP, [5]),
            (CAM_Z_GROUP, [101.615])
        ),
        (
            (CAM_Y_GROUP, [7]),
        ),
        (
            (CAM_Y_GROUP, [9]),
        ),
    )

#@todo save info file with every run