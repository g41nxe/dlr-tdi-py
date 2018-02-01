from common.config import Config
from plot import helper
import numpy as np
import os
import re
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
import math
import json


def gauss2d(xy, A, x0, y0, dx, dy):
    (x, y) = xy

    a = ((x - x0) ** 2) / (2 * dx ** 2)
    b = ((y - y0) ** 2) / (2 * dy ** 2)

    g = A * np.exp( -(a + b) )

    return g.ravel()

def deltas(header, spot, gather):
    x, y = helper.align_data(header, spot, gather)

    pixelCount  = header["PixelCount"]

    line, A   = np.unravel_index(y.argmax(), y.shape)
    start_row = np.maximum(line - int(round(pixelCount / 2)), 0)
    end_row   = np.minimum(line + int(round(pixelCount / 2)), (len(y) - 1))

    ydata = y[start_row:end_row, :]

    cx, cy = np.unravel_index(ydata.argmax(), ydata.shape)

    x0 = ydata[:, cy].mean()
    y0 = ydata[cx, :].mean()
    dx = ydata[:, cy].std()
    dy = ydata[cx, :].std()

    x = np.linspace(1, pixelCount, pixelCount)
    y = np.linspace(1, pixelCount, pixelCount)

    x, y = np.meshgrid(x, y)

    popt, pcov = curve_fit(gauss2d, (x, y), ydata.ravel(), p0=[A, x0, y0, dx, dy])
    return popt

def plot(subdirectory, type):
    data = {}
    for root, dirs, files in os.walk(subdirectory):
        for file in files:
            if (not file.endswith('.spot')):
                continue

            name, ext = os.path.splitext(file)
            if not (name + ".gather") in files:
                continue

            pattern = r"(\d*)_([\w-]*)_#(\d)*"
            m = re.search(pattern, name)

            # old version
            if m is None:
                pattern =  r"(\d*)_(\d*)hz_position(\d+)"
                m = re.search(pattern, name)

            if m is None:
                continue

            h, s = helper.load_spot_file(subdirectory + "\\" + name + '.spot')
            g = helper.load_gathering_file(subdirectory + "\\" + name + '.gather')

            f   = h['LineFreq']
            id  = m.group(1)
            r   = m.group(3)

            if len(s) < 1 or len(g) < 1:
                continue

            try:
                params = deltas(h, s, g)
            except Exception:
                continue

            if id not in data:
                data[id] = {
                    'run': [],
                    'frequency': [],
                    'fwhm_x':   [],
                    'fwhm_y':   [],
                }

            delta_x = abs(params[3])
            delta_y = abs(params[4])

            data[id]['fwhm_x'].append(2 * math.sqrt(2 * np.log(2)) * delta_x)
            data[id]['fwhm_y'].append(2 * math.sqrt(2 * np.log(2)) * delta_y)
            data[id]['frequency'].append(f)
            data[id]['run'].append(r)

    if type == "frequency":
        key   = "frequency"
        label = "Frequency (Hz)"
    else:
        key   = "run"
        label = "Run"

    f, ax = plt.subplots(len(data.items()), sharex=True)
    plt.suptitle(r'Development of FWHM (2D-Gauss-Fit) With Increasing Frequency')

    i = 0
    for id, values in data.items():
        ax.scatter(values[key], values['fwhm_x'], label=r'$FWHM_x$')
        ax.scatter(values[key], values['fwhm_y'], label=r'$FWHM_y$')

        ax.set_title("Run " + id, loc='right', fontsize=9)
        ax.set_ylabel(r'FWHM')
        ax.legend(numpoints=1, loc='upper left')
        i += 1

    ax.set_xlabel(label)
    plt.show()

