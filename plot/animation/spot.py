import numpy as np
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as colors
import collections

from mpl_toolkits.axes_grid1.inset_locator import inset_axes
from matplotlib.animation import FuncAnimation

from common.io import *
from common.gauss import gaussfit

framedata = []
ax = None
cb = None
ymin = ymax = None

def plot(subdirectory, save=False):
    global ax, ymin, ymax

    gauss = loadNPY(subdirectory)

    if save is True or len(gauss) < 1:
        saveNPY(subdirectory, func=buildAndAppendData)
        gauss = loadNPY(subdirectory)

    for id in gauss.keys():
        pixelCount = ymin = ymax = 0

        data = (gauss[id]).tolist()

        for run in sorted(data, key=int):
            values = data[run]
            ymax = max(ymax, np.max(values['ydata']))
            ymin = min(ymin, np.min(values['ydata']))
            pixelCount = max(pixelCount, values['ydata'].shape[0])

            framedata.append({'ydata': values['ydata'], 'popt': values['popt'], 'run': run})

        f, ax = style(pixelCount)

        anim = FuncAnimation(f, frame, frames=np.arange(0, len(framedata)), interval=200)
        anim.save(filename=subdirectory + "\\" + id + ".mp4", dpi=80, writer='ffmpeg')

def buildAndAppendData(id, header, spot, gather, run, data):
    ydata = extractBrightestSpot(header, spot, gather)
    popt  = gaussfit(ydata)

    if id not in data.keys():
        data[id] = {}

    data[id][run.number] = {}
    data[id][run.number]['popt']  = popt
    data[id][run.number]['ydata'] = ydata

    return data

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

def frame(i):
    update(framedata[i]['ydata'], framedata[i]['popt'], framedata[i]['run'])

def update(ydata, popt, id):
    global cb
    norm = colors.Normalize(vmin=ymin, vmax=ymax)
    p = ax.imshow(ydata, cmap=cm.gray, origin="bottom", norm=norm)

    if not cb is None:
        cb.remove()

    cb = colorbar(ax, p)

    ax.set_title("Run " + str(id), loc='right', fontsize=9)
    return
