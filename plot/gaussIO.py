from plot import helper
from common.config import Config
import numpy as np
import math, os
from scipy.optimize import curve_fit
from scipy.interpolate import spline

import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.cm as cm
from mpl_toolkits.axes_grid1.inset_locator import inset_axes

from matplotlib.widgets import Slider

def gauss2d(xy, A, x0, y0, dx, dy):
    (x, y) = xy

    a = ((x - x0) ** 2) / (2 * dx ** 2)
    b = ((y - y0) ** 2) / (2 * dy ** 2)

    g = A * np.exp(-(a + b))

    return g.ravel()

def plot(subdirectory, type):

    gauss = {}
    max_x = 0
    max_y = 0
    pixelCount = 0
    rowCount = 0

    for root, dirs, files in os.walk(subdirectory):
        for file in files:
            if (not file.endswith('.spot')):
                continue

            id, ext = os.path.splitext(file)
            if not (id + ".gather") in files:
                continue

            header, spot = helper.load_spot_file(subdirectory + "\\" + id + '.spot')
            gather = helper.load_gathering_file(subdirectory + "\\" + id + '.gather')

            x, y = helper.align_data(header, spot, gather)
            pixelCount = header["PixelCount"]

            line, A = np.unravel_index(y.argmax(), y.shape)
            start_row = np.maximum(line - int(round(pixelCount / 2)), 0)
            end_row = np.minimum(line + int(round(pixelCount / 2)), (len(y) - 1))

            rowCount = end_row - start_row

            ydata = y[start_row:end_row, :]

            cx, cy = np.unravel_index(ydata.argmax(), ydata.shape)

            x0 = ydata[:, cy].mean()
            y0 = ydata[cx, :].mean()
            dx = ydata[:, cy].std()
            dy = ydata[cx, :].std()

            x = np.arange(rowCount)
            y = np.arange(pixelCount)

            x, y = np.meshgrid(x, y)
            try:
                gauss[id] = {}
                popt, pcov = curve_fit(gauss2d, (x, y), ydata.ravel(), p0=[A, x0, y0, dx, dy])

                gauss[id]['popt']  = popt
                gauss[id]['ydata'] = ydata
                gauss[id]['cx']    = cx
                gauss[id]['cy']    = cy

                max_x = max(max(ydata[:, cy]),  max_x)
                max_y = max( max(ydata[cx, :]), max_y)

            except:
                gauss.pop(id, None)
                pass

    axes = style(max_x, max_y, pixelCount, rowCount)

    for (id, data) in gauss.items():
        cb = update(data['ydata'], data['popt'], rowCount, pixelCount, data['cx'], data['cy'], axes)

        plt.show()

        plt.pause(0.1)

        for ax in axes:
            ax.clear()

        cb.remove()

def style(max_x, max_y, pixelCount, rowCount):

        # plot
        f = plt.figure(figsize=(6, 6))
        gs = gridspec.GridSpec(3, 3, wspace=0.0, hspace=0.0)
        plt.ion()

        ax1 = plt.subplot2grid((3, 3), (1, 0), colspan=2, rowspan=2)
        ax2 = plt.subplot2grid((3, 3), (1, 2), rowspan=2)
        ax3 = plt.subplot2grid((3, 3), (0, 0), colspan=2)
        ax4 = plt.subplot2grid((3, 3), (0, 2))

        ax1.set_aspect('equal')


        ax1.grid(linestyle='dashed', alpha=.3)
        ax2.grid(linestyle='dashed', alpha=.75)
        ax3.grid(linestyle='dashed', alpha=.75)

        ax1.set_xticks(np.arange(0.5, pixelCount, 1))
        ax1.set_yticks(np.arange(0.5, pixelCount, 1))

        ax3.set_xticks(np.arange(0.5, pixelCount, 1))
        ax2.set_yticks(np.arange(0.5, pixelCount, 1))

        ax3.set_xticklabels(np.arange(0, pixelCount, 1), minor=True)
        ax2.set_yticklabels(np.arange(0, pixelCount, 1), minor=True)

        ax3.set_yticks(np.arange(0, max_x, 100))
        ax2.set_xticks(np.arange(0, max_y, 100))

        ax1.set_xticklabels('')
        ax1.set_yticklabels('')

        ax1.set_xticks(np.arange(0, pixelCount, 5), minor=True)
        ax1.set_xticklabels(np.arange(0, pixelCount, 5), minor=True)

        ax1.set_yticks(np.arange(0, pixelCount, 5), minor=True)
        ax1.set_yticklabels(np.arange(0, pixelCount, 5), minor=True)

        ax2.set_yticks(np.arange(0, pixelCount, 1), minor=True)
        ax3.set_xticks(np.arange(0, pixelCount, 1), minor=True)

        ax1.tick_params(axis='both', which='major', length=1.5, right=True, top=True)
        ax1.tick_params(axis='both', which='minor', length=1.5, color='white')

        ax2.tick_params(axis='y', which='major', length=0)
        ax2.tick_params(axis='y', which='minor', length=1.5)
        ax2.tick_params(axis='x', which='major', length=1.5)

        ax3.tick_params(axis='y', which='major', length=1.5)
        ax3.tick_params(axis='x', which='minor', length=1.5)
        ax3.tick_params(axis='x', which='major', length=0)

        plt.setp([
            ax1.get_yminorticklabels(), ax1.get_xminorticklabels(),
            ax2.get_xticklabels(), ax2.get_yticklabels(), ax2.get_xminorticklabels(), ax2.get_yminorticklabels(),
            ax3.get_yticklabels(), ax3.get_xticklabels(), ax3.get_xminorticklabels(), ax3.get_yminorticklabels(),
        ], fontsize=6, linespacing=1)

        plt.setp([
            ax2.get_yminorticklabels(),
            ax3.get_xminorticklabels(),
            ax2.get_yticklabels(),
            ax3.get_xticklabels()
        ], visible=False)

        ax1.set_xlim(-0.5, pixelCount - 0.5)
        ax1.set_ylim(-0.5, pixelCount - 0.5)
        ax2.set_ylim(-0.5, pixelCount - 0.5)
        ax3.set_xlim(-0.5, pixelCount - 0.5)

        plt.suptitle('Spot-Image with 2D-Gaussian Fit')

        ax4.axis('off')

        return (ax1, ax2, ax3, ax4)

def colorbar(ax1, p):
    cax = inset_axes(ax1, width="95%", height="3%", loc=9)
    c = plt.colorbar(p, cax=cax, orientation="horizontal")

    c.ax.tick_params(labelsize=6, color='#cccccc')
    c.outline.set_edgecolor('#cccccc')

    cxtick = plt.getp(c.ax.axes, 'yticklabels')
    cytick = plt.getp(c.ax.axes, 'xticklabels')
    plt.setp([cxtick, cytick], color='#cccccc')

    return c

def update(ydata, popt, rowCount, pixelCount, cx, cy, axes):

    (ax1, ax2, ax3, ax4) = axes

    x = np.arange(rowCount)
    y = np.arange(pixelCount)

    x, y = np.meshgrid(x, y)
    ydata_fitted = gauss2d((x, y), *popt)
    ydata_fitted = ydata_fitted.reshape(pixelCount, pixelCount)

    p = ax1.imshow(ydata, cmap=cm.gray, origin="bottom")
    ax2.scatter(ydata[:, cy], np.arange(rowCount), alpha=0.6, s=10, color='black')

    ax2.plot(spline(np.arange(pixelCount), ydata_fitted[:, cy], np.linspace(0, pixelCount, 100)),
             np.linspace(0, pixelCount, 100), color='black', alpha=0.4)

    ax3.scatter(np.arange(pixelCount), ydata[cx, :], alpha=0.6, s=10, color='black')

    ax3.plot(np.linspace(0, pixelCount, 100),
             spline(np.arange(pixelCount), ydata_fitted[cx, :], np.linspace(0, pixelCount, 100)), color='black',
             alpha=0.4)

    cb = colorbar(ax1, p)

    return cb

