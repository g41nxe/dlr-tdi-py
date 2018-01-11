from plot import helper
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import argrelextrema

def plot(header, spot, gather):

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

