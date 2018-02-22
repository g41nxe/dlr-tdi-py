from common.io import *
from common.gauss import gaussfit, gauss2d

import numpy as np
from scipy.interpolate import spline

import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.cm as cm
from mpl_toolkits.axes_grid1.inset_locator import inset_axes

def plot(header, spot, gather):
    ydata      = extractBrightestSpot(header, spot, gather)
    pixelCount = ydata.shape[0]
    rowCount   = ydata.shape[1]

    x = np.linspace(1, pixelCount, pixelCount)
    y = np.linspace(1, pixelCount, pixelCount)
    x, y = np.meshgrid(x, y)

    cx, cy     = np.unravel_index(ydata.argmax(), ydata.shape)

    # plot
    f = plt.figure(figsize=(6, 6))
    gs = gridspec.GridSpec(3, 3, wspace=0.0, hspace=0.0)

    ax1 = plt.subplot2grid((3, 3), (1, 0), colspan=2, rowspan=2)
    ax2 = plt.subplot2grid((3, 3), (1, 2), rowspan=2)
    ax3 = plt.subplot2grid((3, 3), (0, 0), colspan=2)
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

    ax1.grid(linestyle='dashed', alpha=.3)
    ax2.grid(linestyle='dashed', alpha=.75)
    ax3.grid(linestyle='dashed', alpha=.75)

    ax1.set_xticks(np.arange(0.5, pixelCount, 1))
    ax1.set_yticks(np.arange(0.5, pixelCount, 1))

    ax3.set_xticks(np.arange(0.5, pixelCount, 1))
    ax2.set_yticks(np.arange(0.5, pixelCount, 1))

    ax3.set_xticklabels(np.arange(0, pixelCount, 1), minor=True)
    ax2.set_yticklabels(np.arange(0, pixelCount, 1), minor=True)

    ax3.set_yticks(np.arange(0, max(ydata[:, cy]), 100))
    ax2.set_xticks(np.arange(0, max(ydata[cx, :]), 100))

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

    try:
        popt = gaussfit(ydata)
    except Exception as e:
        raise e


    ydata_fitted = gauss2d((x, y), *popt)
    ydata_fitted = ydata_fitted.reshape(pixelCount, pixelCount)

    ax2.plot(spline(np.arange(pixelCount), ydata_fitted[:, cy], np.linspace(0, pixelCount, 100)),
             np.linspace(0, pixelCount, 100), color='black', alpha=0.4)

    ax3.plot(np.linspace(0, pixelCount, 100),
             spline(np.arange(pixelCount), ydata_fitted[cx, :], np.linspace(0, pixelCount, 100)), color='black',
             alpha=0.4)

    text = r'$\sigma_x = ' + str(round(popt[3], 4)) + "$\n" \
           + '$\sigma_y = ' + str(round(popt[4], 4)) + "$\n" \
           + '$x_0 = ' + str(round(popt[1], 4)) + "$\n" \
           + '$y_0 = ' + str(round(popt[2], 4)) + "$\n" \
           + '$A = ' + str(round(popt[0], 4)) + "$\n" \
           + r'$\theta = ' + str(round(popt[5], 4)) + "$\n"

    ax4.text(0.25, 0.25, text, fontsize=8)



    plt.suptitle('Spot-Image with 2D-Gaussian Fit')

    ax4.axis('off')
