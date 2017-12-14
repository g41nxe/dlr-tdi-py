from common.config import Config
from plot import helper
import numpy as np
import os
import re
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt


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

            m = re.search(r"(\d*)_(\d*)hz_position(\d*)", name)
            if m is None:
                continue

            id     = m.group(1)
            f      = int(m.group(2))
            p      = int(m.group(3))

            h, s   = helper.load_spot_file(subdirectory + "\\" + name + '.spot')
            g      = helper.load_gathering_file(subdirectory + "\\" + name + '.gather')

            if len(s) < 1 or len(g) < 1:
                continue

            if id not in data:
                data[id] = {
                    'position'  : [],
                    'frequency' : [],
                    'delta_x'   : [],
                    'delta_y'   : [],
                }

            params = deltas(h, s, g)

            data[id]['delta_x'].append(params[3])
            data[id]['delta_y'].append(params[4])
            data[id]['position'].append(p)
            data[id]['frequency'].append(f)

    if type in "frequency":
        key   = "frequency"
        label = "Frequency (Hz)"
    else:
        key   = "position"
        label = "Position"

    f, ax = plt.subplots(len(data), sharex=True)
    plt.suptitle(r'Development of $\delta_x$ and $\delta_y$ with increasing frequency')

    i = 0
    for id, values in data.items():
        ax[i].plot(values[key], values['delta_x'], label=r'$\delta_x$')
        ax[i].plot(values[key], values['delta_y'], label=r'$\delta_y$')

        ax[i].set_title("Run " + id, loc='right', fontsize=9)
        ax[i].set_ylabel(r'$\delta$')
        ax[i].legend(numpoints=1, loc='upper left')
        i += 1

    ax[i-1].set_xlabel(label)

