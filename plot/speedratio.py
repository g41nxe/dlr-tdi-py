from plot import helper
from scipy.optimize import curve_fit
from common.logger import Logger
import numpy as np
import os, re, math
import matplotlib.pyplot as plt
from control.run import RunConfig, Run
from common.util import get_vel_from_freq as vel

def gauss2d(xy, A, x0, y0, sigma_x, sigma_y, theta):
    (x, y) = xy

    a =  math.cos(  theta)**2 / (2 * sigma_x ** 2) + math.sin(  theta)**2 / (2*sigma_y**2)
    b = -math.sin(2*theta)    / (4 * sigma_x ** 2) + math.sin(2*theta)    / (4*sigma_y**2)
    c =  math.sin(  theta)**2 / (2 * sigma_x ** 2) + math.cos(  theta)**2 / (2*sigma_y**2)

    g =  A * np.exp( - (a*(x-x0)**2 + 2*b*(x-x0)*(y-y0) + c*(y-y0)**2))

    return g.ravel()

def initial(data):

    cx, cy  = np.unravel_index(data.argmax(), data.shape)
    A       = data[cx, cy]
    sigma_x = np.sqrt(data[cx, :].std())
    sigma_y = np.sqrt(data[:, cy].std())

    total = data.sum()

    X, Y = np.indices(data.shape)

    Mxx = np.ma.sum((X - cx) * (X - cx) * data) / total
    Myy = np.ma.sum((Y - cy) * (Y - cy) * data) / total
    Mxy = np.ma.sum((X - cx) * (Y - cy) * data) / total

    rot = 0.5 * np.arctan(2 * Mxy / (Mxx - Myy))

    return A, cx, cy, sigma_x, sigma_y, rot

def gaussfit(header, spot, gather):
    x, y = helper.align_data(header, spot, gather)

    pixelCount  = header["PixelCount"]

    line, col = np.unravel_index(y.argmax(), y.shape)
    start_row = np.maximum(line - int(round(pixelCount / 2)), 0)
    end_row   = np.minimum(line + int(round(pixelCount / 2)), (len(y) - 1))
    ydata     = y[start_row:end_row, :]

    x, y = np.meshgrid(np.linspace(1, pixelCount, pixelCount), np.linspace(1, pixelCount, pixelCount))

    popt, pcov = curve_fit(gauss2d, (x, y), ydata.ravel(),
                                          p0=initial(ydata),
                                          bounds=([0, 0, 0, 0, 0, -math.pi], [5000, 32, 32, np.inf, np.inf, math.pi]))
    return popt

def fwhm(x):
    return 2 * math.sqrt(2 * np.log(2)) * abs(x)

def plot(subdirectory, save=False):

    if save is True:
        data = saveToNPY(subdirectory)

    data = loadFromNPY(subdirectory)

    f, ax = plt.subplots(3, sharex=True)
    plt.suptitle(r'Development of $\sigma_x$ and $\sigma_y$ of 2D-Gauss-Fit with changing speed-ratio')

    for i, values in data.items():
        values = values.tolist()
        label = str(int(values['vel'][0] / 0.00875)) + " Hz"

        ax[0].scatter(values['speed-ratio'], values['delta_x'], label=label, alpha=.75, s=10)
        ax[0].legend(numpoints=1, loc='upper left')
        ax[0].grid()
        ax[0].set_ylim([0, 5])
        ax[0].set_ylabel("$\sigma_x$")

        ax[1].scatter(values['speed-ratio'], values['delta_y'], label=label, alpha=.75, s=10)
        ax[1].legend(numpoints=1, loc='upper left')
        ax[1].grid()
        ax[1].set_ylim([0,11])
        ax[1].set_ylabel("$\sigma_y$")

        ax[2].scatter(values['speed-ratio'], values['theta'], label=label, alpha=.75, s=10)
        ax[2].legend(numpoints=1, loc='upper left')
        ax[2].grid()
        ax[2].set_ylim([-math.pi, math.pi])
        ax[2].set_ylabel(r"$\theta$")

        ax[2].set_xlabel("Speed ratio")

    plt.show()

def loadFromNPY(subdirectory):
    data = {}

    for root, dirs, files in os.walk(subdirectory):
        for file in files:
            if (not file.endswith('.npy')):
                continue

            name, ext = os.path.splitext(file)
            data[name] = np.load(os.path.join(root,file))

    return data

def loadRuns():
    runs = {}

    for root, dirs, files in os.walk(os.path.dirname(os.path.abspath(__file__)) + "\\..\\tasks\\" ):
        for file in files:
            name, ext = os.path.splitext(file)
            if not (name + ".json") in files:
                continue

            Logger.get_logger().info("Loading task %s", name)
            taskfile = os.path.join(root, name) + '.json'
            cfg = RunConfig(taskfile)
            runs[name] = {}
            runs[name] = cfg.getRuns()

    return runs

def saveToNPY(subdirectory):

    data = {}
    runs = loadRuns()

    for root, dirs, files in os.walk(subdirectory):
        for file in files:
            if (not file.endswith('.spot')):
                continue

            name, ext = os.path.splitext(file)
            if not (name + ".gather") in files:
                continue

            pattern = r"(\d*)_([\d\w-]*)_(\d*)"
            m = re.search(pattern, name)

            if m is None:
                continue

            id   = m.group(1)
            task = m.group(2)
            run  = m.group(3)

            Logger.get_logger().info("Loading %s", name)

            header, spot = helper.load_spot_file(os.path.join(root, name) + '.spot')
            gather       = helper.load_gathering_file(os.path.join(root, name) + '.gather')
            f            = header['LineFreq']

            if not task in runs.keys():
                Logger.get_logger().warn("Task %s not found", task)

            try:
                params = gaussfit(header, spot, gather)
            except Exception as e:
                print(e)
                continue

            if id not in data:
                data[id] = {
                    'fwhm_x': [],
                    'fwhm_y': [],
                    'vel': [],
                    'delta_x': [],
                    'delta_y': [],
                    'freq': [],
                    'run': [],
                    'speed-diff': [],
                    'speed-ratio': [],
                    'theta': [],
                }

            data[id]['fwhm_x'].append( fwhm(params[3]) )
            data[id]['fwhm_y'].append( fwhm(params[4]) )
            data[id]['vel'].append( runs[task][int(run)].vel )
            data[id]['delta_x'].append( params[3] )
            data[id]['delta_y'].append( params[4] )
            data[id]['freq'].append( f )
            data[id]['run'].append(run)
            data[id]['speed-diff'].append( runs[task][int(run)].vel - vel(f) )
            data[id]['speed-ratio'].append( round(vel(f) / runs[task][int(run)].vel, 2) )
            data[id]['theta'].append(params[5])

    for id in data.keys():
        f = subdirectory + "\\" + id
        np.save(f, data[id])

    return data