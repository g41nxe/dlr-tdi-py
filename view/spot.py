import matplotlib.pyplot as plt
from common.config import Config

def plot(header, spot, gather):

    fig, ax      = plt.subplots()
    pcm          = ax.pcolormesh(spot, cmap='Greys_r', vmin=0, vmax=Config.CLAMP_INTENSITY)

    plt.xlabel('Pixel')
    plt.ylabel('Line')

    fig.colorbar(pcm, ax=ax)
    plt.tight_layout()
    plt.show()