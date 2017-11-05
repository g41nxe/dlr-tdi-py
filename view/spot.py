import matplotlib.pyplot as plt

def plot(header, spot, gather):

    fig, ax      = plt.subplots()
    pcm          = ax.pcolormesh(spot, cmap='Greys_r', vmin=0, vmax=2000)

    plt.xlabel('Pixel')
    plt.ylabel('Line')

    fig.colorbar(pcm, ax=ax)
    plt.tight_layout()
    plt.show()