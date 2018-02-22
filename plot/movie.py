from plot import helper
from common.logger import Logger
import numpy as np
import math, os, re, json
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as colors
from mpl_toolkits.axes_grid1.inset_locator import inset_axes
from matplotlib.animation import FuncAnimation

framedata = []
ax = None
cb = None
ymin = ymax = None

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

    for item in os.listdir(subdirectory):
        if not os.path.isfile(os.path.join(subdirectory, item)):
            continue

        if not item.endswith('.npy'):
            continue

        name, ext = os.path.splitext(item)
        data[name] = np.load(os.path.join(subdirectory, item))

    return data

def frame(i):
    update(framedata[i]['ydata'], framedata[i]['popt'], framedata[i]['run'])

def plot(subirectory, save=False):
    global ax, ymin, ymax

    gauss = loadNPY(subirectory)

    if save is True or len(gauss) < 1:
        saveNPY(subirectory)
        gauss = loadNPY(subirectory)

    for id in gauss.keys():
        pixelCount = ymin = ymax = 0

        for (run, values) in (gauss[id]).tolist()[int(id)].items():
            ymax = max(ymax, np.max(values['ydata']))
            ymin = min(ymin, np.min(values['ydata']))
            pixelCount = max(pixelCount, values['ydata'].shape[0])

            framedata.append({'ydata': values['ydata'], 'popt': values['popt'], 'run': run})

        f, ax = style(pixelCount)

        anim = FuncAnimation(f, frame, frames=np.arange(0, len(framedata)), interval=200)
        anim.save(filename=subirectory + "\\" + id + ".mp4", dpi=80, writer='ffmpeg')


def style(pixelCount):
    f, axis = plt.subplots(1)

    axis.grid(linestyle='dashed', alpha=.3)

    axis.set_xticks(np.arange(0.5, pixelCount, 1))
    axis.set_yticks(np.arange(0.5, pixelCount, 1))

    axis.set_xticklabels('')
    axis.set_yticklabels('')

    axis.set_xticks(np.arange(0, pixelCount, 5), minor=True)
    axis.set_xticklabels(np.arange(0, pixelCount, 5), minor=True)

    axis.set_yticks(np.arange(0, pixelCount, 5), minor=True)
    axis.set_yticklabels(np.arange(0, pixelCount, 5), minor=True)

    axis.tick_params(axis='both', which='major', length=1.5, right=True, top=True)
    axis.tick_params(axis='both', which='minor', length=1.5, color='white')

    plt.setp([
        axis.get_yminorticklabels(), axis.get_xminorticklabels(),
    ], fontsize=6, linespacing=1)

    axis.set_xlim(-0.5, pixelCount - 0.5)
    axis.set_ylim(-0.5, pixelCount - 0.5)

    plt.suptitle('Spot-Image with 2D-Gaussian Fit')

    return f, axis

def colorbar(ax, p):

    cax = inset_axes(ax, width="95%", height="3%", loc=9)

    c = plt.colorbar(p, cax=cax, orientation="horizontal")

    c.ax.tick_params(labelsize=6, color='#cccccc')
    c.outline.set_edgecolor('#cccccc')

    cxtick = plt.getp(c.ax.axes, 'yticklabels')
    cytick = plt.getp(c.ax.axes, 'xticklabels')
    plt.setp([cxtick, cytick], color='#cccccc')

    return c

def update(ydata, popt, id):
    global cb
    norm = colors.Normalize(vmin=ymin, vmax=ymax)
    p = ax.imshow(ydata, cmap=cm.gray, origin="bottom", norm=norm)

    if not cb is None:
        cb.remove()

    cb = colorbar(ax, p)

    ax.set_title("Run " + str(id), loc='right', fontsize=9)
    return
