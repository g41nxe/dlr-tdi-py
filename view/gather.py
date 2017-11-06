import matplotlib.pyplot as plt

def plot(header, spot, gather):

    position = gather[:, 0]
    speed    = gather[:, 1]
    x        = range(0, len(position))

    # Two subplots, the axes array is 1-d

    s = 0.5
    ax1 = plt.subplot(211)
    ax1.scatter(x, position, s=s)
    ax1.set_ylabel('Line')
    ax1.set_ylabel('Position (mm)')
    ax1.set_title('Position and Velocity')

    ax2 =  plt.subplot(212, sharex=ax1)
    ax2.scatter(x, speed, s=s)
    ax2.set_ylabel('Velocity (m/s)')

    plt.setp(ax2.get_xticklabels(), fontsize=6)
    plt.setp(ax1.get_xticklabels(), visible=False)
    plt.tight_layout()
    plt.show()
