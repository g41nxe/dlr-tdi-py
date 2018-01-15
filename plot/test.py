from plot import helper
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import argrelextrema
import matplotlib.gridspec as gridspec
import matplotlib.cm as cm
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

def plot2(header, spot, gather):

    x, y = helper.align_data(header, spot, gather)

    max_value_per_row       = np.max(y, 1)
    row_w_max_value         = np.argmax(max_value_per_row)
    px_w_max_value_per_row  = np.argmax(y, 1)

    max_px                  = px_w_max_value_per_row[row_w_max_value]

    y = y[:, max_px]
    # x = gather[:, 0]
    # y = spot[:, max_px]

    local_max = np.array(argrelextrema(x, np.greater_equal, order=30)).ravel()
    max_intensities = []

    for i in range(1, len(local_max)):

        i1 = local_max[i-1]
        i2 = local_max[i]

        v, i = y[i1:i2].max(), y[i1:i2].argmax()
        max_intensities.append(i+i1)

    plt.scatter(max_intensities, x[max_intensities], color='r')
    plt.plot(x)

    plt.title('Position of max. Intensities vs. XPS Position')
    plt.ylabel('Position (mm)')
    plt.xlabel('Line')

def plot(header, spot, gather):
    x, y = helper.align_data(header, spot, gather)


    ax1 = plt.subplot()
    print (y.shape)
    p = ax1.imshow(np.transpose(y[0:500,:]), cmap=cm.gray, origin="bottom")

    cax = inset_axes(ax1, width="95%", height="3%", loc=9)
    c = plt.colorbar(p, cax=cax, orientation="horizontal")

    c.ax.tick_params(labelsize=6, color='#cccccc')
    c.outline.set_edgecolor('#cccccc')


