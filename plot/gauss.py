from plot import helper
from common.config import Config
import numpy as np
import math
from scipy.optimize import curve_fit
from scipy.interpolate import spline

import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.cm as cm
from mpl_toolkits.axes_grid1.inset_locator import inset_axes

import matplotlib.colors as colors
from mpl_toolkits.axes_grid.anchored_artists import AnchoredText


def gauss2d(xy, A, x0, y0, dx, dy):
    (x, y) = xy

    a = ((x - x0) ** 2) / (2 * dx ** 2)
    b = ((y - y0) ** 2) / (2 * dy ** 2)

    g = A * np.exp( -(a + b) )

    return g.ravel()

def plot(header, spot, gather):
    x, y = helper.align_data(header, spot, gather)
    print(x.shape)
    print(y.shape)
    pixelCount  = header["PixelCount"]

    line, A   = np.unravel_index(y.argmax(), y.shape)
    start_row = np.maximum(line - int(round(pixelCount / 2)), 0)
    end_row   = np.minimum(line + int(round(pixelCount / 2)), (len(y) - 1))

    rowCount  = end_row - start_row

    ydata = y[start_row:end_row, :]

    cx, cy = np.unravel_index(ydata.argmax(), ydata.shape)

    x0 = ydata[:, cy].mean()
    y0 = ydata[cx, :].mean()
    dx = ydata[:, cy].std()
    dy = ydata[cx, :].std()

    x = np.arange(rowCount)
    y = np.arange(pixelCount)

    x, y = np.meshgrid(x, y)

    # plot
    f   = plt.figure(figsize=(6,6))
    gs  = gridspec.GridSpec(3,3, wspace=0.0, hspace=0.0)

    ax1 = plt.subplot2grid((3, 3), (1, 0), colspan=2, rowspan=2)
    ax2 = plt.subplot2grid((3, 3), (1, 2), rowspan=2, sharey=ax1)
    ax3 = plt.subplot2grid((3, 3), (0, 0), colspan=2, sharex=ax1)
    ax4 = plt.subplot2grid((3, 3), (0, 2))

    p = ax1.imshow(ydata, cmap=cm.gray, origin="bottom")
    ax2.scatter(ydata[:, cy], np.arange(rowCount), alpha=0.6, s=10, color='black')
    ax3.scatter(np.arange(pixelCount), ydata[cx, :], alpha=0.6, s=10, color='black')

    ax1.set_aspect('equal')

    cax = inset_axes(ax1, width="95%", height="3%", loc=9)
    c = plt.colorbar(p, cax=cax, orientation="horizontal")

    c.ax.tick_params(labelsize=6, color='#cccccc')
    c.outline.set_edgecolor('#cccccc')

    cxtick = plt.getp(c.ax.axes, 'yticklabels')
    cytick = plt.getp(c.ax.axes, 'xticklabels')
    plt.setp([cxtick, cytick], color='#cccccc')

    plt.setp([ax1.get_yticklabels(), ax2.get_yticklabels(), ax3.get_yticklabels()], fontsize=6)
    plt.setp([ax1.get_xticklabels(), ax2.get_xticklabels(), ax3.get_xticklabels()], fontsize=6)
    plt.setp([ax2.get_yticklabels(), ax3.get_xticklabels()], visible=False)

    ax1.set_xlim(0, pixelCount-1)
    ax1.set_ylim(0, pixelCount-1)
    ax2.set_ylim(0, pixelCount-1)
    ax3.set_xlim(0, pixelCount-1)

    try:
        popt, pcov   = curve_fit(gauss2d, (x, y), ydata.ravel(), p0=[A, x0, y0, dx, dy])
        ydata_fitted = gauss2d((x, y), *popt)
        ydata_fitted = ydata_fitted.reshape(pixelCount, pixelCount)

        ax2.plot(spline(np.arange(pixelCount), ydata_fitted[:, cy], np.linspace(0, pixelCount, 100)), np.linspace(0, pixelCount, 100), color='black', alpha=0.4)

        ax3.plot(np.linspace(0, pixelCount, 100), spline(np.arange(pixelCount), ydata_fitted[cx, :], np.linspace(0, pixelCount, 100)), color='black', alpha=0.4)

        text = r'$\delta_x = ' + str(round(popt[3], 4)) + "$\n" \
               + '$\delta_y = ' + str(round(popt[4], 4)) + "$\n" \
               + '$x_0 = ' + str(round(popt[1], 4)) + "$\n" \
               + '$y_0 = ' + str(round(popt[2], 4)) + "$\n" \
               + '$A = ' + str(round(popt[0], 4)) + "$\n" \

        ax4.text(0.25, 0.25, text, fontsize=8)

    except:
        pass

    plt.suptitle('Spot-Image with 2D-Gaussian Fit')

    ax4.axis('off')

