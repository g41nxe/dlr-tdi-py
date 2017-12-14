import matplotlib.pyplot as plt
from common.config import Config
from plot import helper

import numpy as np
def plot(header, spot, gather):

    #x, y = helper.align_data(header, spot, gather)
    y = spot

    fig, ax = plt.subplots()

    ax.scatter(np.linspace(1, len(y), len(y)), y.mean(axis=1), s=0.5)

    plt.xlabel('Pixel')
    plt.ylabel('Intensity')
    plt.title('Intensity')
    plt.ylim(0, Config.CLAMP_MAX_INTENSITY)

    #fig.colorbar(pcm, ax=ax)
    plt.show()