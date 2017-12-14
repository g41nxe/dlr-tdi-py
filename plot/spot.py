import matplotlib.pyplot as plt
from common.config import Config
from plot import helper

import numpy as np
def plot(header, spot, gather):

    #x, y = helper.align_data(header, spot, gather)
    y = spot

    fig, ax = plt.subplots()

    ax.scatter(np.linspace(1, len(y), np.size(y, 0)), y.mean(axis=1), s=1)

    plt.xlabel('Line')
    plt.ylabel('mean intensity of all pixels')
    plt.title('Intensity')
    plt.ylim(Config.CLAMP_MIN_INTENSITY, Config.CLAMP_MAX_INTENSITY)
    textstr = "clamp min: " + str(Config.CLAMP_MIN_INTENSITY) + "\n" \
            + "clamp max: " + str(Config.CLAMP_MAX_INTENSITY)

    props = dict(boxstyle='round', facecolor='white', alpha=0.5)
    ax.text(0.05, 0.95, textstr, transform=ax.transAxes, fontsize=9, verticalalignment='top', bbox=props)


    #fig.colorbar(pcm, ax=ax)
