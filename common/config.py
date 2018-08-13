import logging

class Config:
    data = {
        "CAM_HOST":         "192.168.0.77",
        "CAM_PORT":         8089,
        "CAM_X_GROUP":      "GROUP2",
        "CAM_Y_GROUP":      "GROUP5",
        "CAM_Z_GROUP":      "GROUP4",
        "CAM_RESULT_PATH":  "G:\\data\\messdaten",
        "CAM_PROGRAM_PATH": "G:\\Projekte\\01_9kDEMO\\SOFTWARE\\Kari\\TDI_9k\\TDI_9k_Demo_100429.exe",

        "XPS_HOST":         "192.168.0.254",
        "XPS_PORT":         5001,
        "XPS_FTP_PATH":     "public",
        "XPS_FTP_FILE":     "Gathering.dat",
        "XPS_USER":         "Administrator",
        "XPS_PASSWORD":     "Administrator",
        "XPS_RESULT_PATH":  "T:\\messdaten",
        "XPS_TRIGGER":      "GPIO1.DI.DILowHigh",
        "XPS_DATA_TYPES":   ["CurrentPosition", "CurrentVelocity"],

        "FP_GROUP":         "GROUP3",
        "FP_GROUP_NAME":    "POSITIONER",
        "FP_START":         -10,            # mm
        "FP_END":           10,             # mm
        "FP_VELOCITY":      81,             # mm/s
        "FP_ACCELERATION":  1500,           # mm/s^2,
        "FP_JERKTIME":      [0.02, 0.02],   # min, max:
        "LOG_LEVEL":        logging.INFO,

        "ITERATIONS":       30,

        "CLAMP_MAX_INTENSITY": 2500,  # intensities > value are outliers
        "CLAMP_MIN_INTENSITY": 0,  # intensities < value are noise

        "PLOT_DATA_FOLDER":     "E:\\Projects\\Repositories\\dlr-tdi-data\\",
        "PLOT_DEFAULT_FILE":    "010218\\speed-55\\152841_speed-55_40",
    }

    @staticmethod
    def set(key, value):
        if key in Config.data:
            Config.data[key] = value

    @staticmethod
    def get(key):
        if key in Config.data:
            return Config.data[key]