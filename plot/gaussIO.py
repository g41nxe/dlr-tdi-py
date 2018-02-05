from plot import helper
from common.logger import Logger
import numpy as np
import math, os, re, json
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from mpl_toolkits.axes_grid1.inset_locator import inset_axes

def gauss2d(xy, A, x0, y0, sigma_x, sigma_y, theta):
    (x, y) = xy

    a = math.cos(theta) ** 2 / (2 * sigma_x ** 2) + math.sin(theta) ** 2 / (2 * sigma_y ** 2)
    b = -math.sin(2 * theta) / (4 * sigma_x ** 2) + math.sin(2 * theta) / (4 * sigma_y ** 2)
    c = math.sin(theta) ** 2 / (2 * sigma_x ** 2) + math.cos(theta) ** 2 / (2 * sigma_y ** 2)

    g = A * np.exp(- (a * (x - x0) ** 2 + 2 * b * (x - x0) * (y - y0) + c * (y - y0) ** 2))

    return g.ravel()

def initial(data):
    cx, cy = np.unravel_index(data.argmax(), data.shape)
    A = data[cx, cy]
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

    pixelCount = header["PixelCount"]

    line, col = np.unravel_index(y.argmax(), y.shape)
    start_row = np.maximum(line - int(round(pixelCount / 2)), 0)
    end_row = np.minimum(line + int(round(pixelCount / 2)), (len(y) - 1))
    ydata = y[start_row:end_row, :]

    x, y = np.meshgrid(np.linspace(1, pixelCount, pixelCount), np.linspace(1, pixelCount, pixelCount))

    try:
        popt, pcov = curve_fit(gauss2d, (x, y), ydata.ravel(),
                               p0=initial(ydata),
                               bounds=([0, 0, 0, 0, 0, -math.pi], [5000, 32, 32, np.inf, np.inf, math.pi]))
    except ValueError:
        try:
            popt, pcov = curve_fit(gauss2d, (x, y), ydata.ravel(),
                                   p0=initial(ydata))
        except Exception as e:
            raise e


    return popt, ydata

def saveNPY(subdirectory):
    data = {}

    for root, dirs, files in os.walk(subdirectory):
        for file in files:
            if (not file.endswith('.spot')):
                continue

            name, ext = os.path.splitext(file)
            if not (name + ".gather") in files:
                continue

            Logger.get_logger().info("Loading file " + name)

            pattern = r"(\d*)_([\d\w-]*)_(\d*)"
            m = re.search(pattern, name)

            if m is None:
                continue

            run = int(m.group(3))
            id  = int(m.group(1))

            header, spot = helper.load_spot_file(subdirectory + "\\" + name + '.spot')
            gather = helper.load_gathering_file(subdirectory + "\\" + name + '.gather')

            try:
                popt, ydata = gaussfit(header, spot, gather)
            except Exception as e:
                print(e)
                continue

            if id not in data.keys():
                data[id] = {}

            data[id][run] = {}
            data[id][run]['popt'] = popt
            data[id][run]['ydata'] = ydata

    for id in data.keys():
        f = subdirectory + "\\" + str(id)
        np.save(f, data)
        Logger.get_logger().info("Save file %s", id)

def loadNPY(subdirectory):
    data = {}

    for root, dirs, files in os.walk(subdirectory):
        for file in files:
            if (not file.endswith('.npy')):
                continue

            name, ext = os.path.splitext(file)
            data[name] = np.load(os.path.join(root, file))

    return data

def plot(subirectory, save=True):

    if save is True:
        saveNPY(subirectory)

    gauss = loadNPY(subirectory)

    ax = style()

    for id in gauss.keys():
        for (run, values) in (gauss[id]).tolist()[int(id)].items():

            cb = update(values['ydata'], values['popt'], ax, run)
            plt.show()

            plt.pause(0.05)
            ax.clear()
            cb.remove()

    while True:
        plt.pause(0.01)

def style(pixelCount=32):
    # plot
    f, ax = plt.subplots(1)
    plt.ion()

    ax.grid(linestyle='dashed', alpha=.3)

    ax.set_xticks(np.arange(0.5, pixelCount, 1))
    ax.set_yticks(np.arange(0.5, pixelCount, 1))

    ax.set_xticklabels('')
    ax.set_yticklabels('')

    ax.set_xticks(np.arange(0, pixelCount, 5), minor=True)
    ax.set_xticklabels(np.arange(0, pixelCount, 5), minor=True)

    ax.set_yticks(np.arange(0, pixelCount, 5), minor=True)
    ax.set_yticklabels(np.arange(0, pixelCount, 5), minor=True)

    ax.tick_params(axis='both', which='major', length=1.5, right=True, top=True)
    ax.tick_params(axis='both', which='minor', length=1.5, color='white')

    plt.setp([
        ax.get_yminorticklabels(), ax.get_xminorticklabels(),
    ], fontsize=6, linespacing=1)

    ax.set_xlim(-0.5, pixelCount - 0.5)
    ax.set_ylim(-0.5, pixelCount - 0.5)

    plt.suptitle('Spot-Image with 2D-Gaussian Fit')

    return ax

def colorbar(ax, p):
    cax = inset_axes(ax, width="95%", height="3%", loc=9)
    c = plt.colorbar(p, cax=cax, orientation="horizontal")

    c.ax.tick_params(labelsize=6, color='#cccccc')
    c.outline.set_edgecolor('#cccccc')

    cxtick = plt.getp(c.ax.axes, 'yticklabels')
    cytick = plt.getp(c.ax.axes, 'xticklabels')
    plt.setp([cxtick, cytick], color='#cccccc')

    return c

def update(ydata, popt, ax, id):
    p = ax.imshow(ydata, cmap=cm.gray, origin="bottom")
    ax.set_title("Run " + str(id), loc='right', fontsize=9)

    ax.set
    cb = colorbar(ax, p)
    return cb
