from plot import helper
import numpy as np
import math
from scipy.optimize import curve_fit
import matplotlib.pyplot as plt
import matplotlib.cm as cm
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

    print([A, x0, dx, y0, dy])

    x = np.linspace(1, pixelCount, pixelCount)
    y = np.linspace(1, pixelCount, pixelCount)

    x, y = np.meshgrid(x, y)

    f, (ax1, ax2, ax3) = plt.subplots(1, 3)


    p1 = ax1.imshow(ydata, cmap=cm.magma, aspect="equal", origin="bottom")
    c1 = f.colorbar(p1, ax=ax1, shrink=0.45)

    f.set_size_inches(12.0, 6.0, True)

    plt.setp(ax1.get_xticklabels(), fontsize=6)
    plt.setp(ax1.get_yticklabels(), fontsize=6)

    c1.ax.tick_params(labelsize=6)

    ax1.set_title("Brightest Spot")

    try:
        popt, pcov = curve_fit(gauss2d, (x, y), ydata.ravel(), p0=[A, x0, y0, dx, dy])
        ydata_fitted = gauss2d((x, y), *popt)
        ydata_fitted = ydata_fitted.reshape(pixelCount, pixelCount)

        p2 = ax2.imshow(ydata_fitted, cmap=cm.magma, aspect="equal", origin="bottom")
        p3 = ax3.imshow(ydata_fitted - ydata, cmap=cm.magma, interpolation="gaussian", aspect="equal", origin="bottom",
                        extent=(x.min(), x.max(), y.min(), y.max()))

        c2 = f.colorbar(p2, ax=ax2, shrink=0.45)
        c3 = f.colorbar(p3, ax=ax3, shrink=0.45)

        plt.setp(ax2.get_xticklabels(), fontsize=6)
        plt.setp(ax2.get_yticklabels(), fontsize=6)
        plt.setp(ax3.get_xticklabels(), fontsize=6)
        plt.setp(ax3.get_yticklabels(), fontsize=6)

        c2.ax.tick_params(labelsize=6)
        c3.ax.tick_params(labelsize=6)

        ax2.set_title("2D-Gauss")
        ax3.set_title("Difference")

        at = AnchoredText(r'$\delta_x = ' + str(round(popt[2], 4)) + "$\n" + '$\delta_y =' + str(round(popt[4], 4)) + '$', prop=dict(size=6), frameon=True, loc=4)
        at.patch.set_boxstyle("round, pad=0.3, rounding_size=0.1")
        ax2.add_artist(at)
    except:
        pass

