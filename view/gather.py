import matplotlib.pyplot as plt

def plot(header, spot, gather):

    position = gather[:, 0]
    speed    = gather[:, 1]
    x        = range(0, len(position))

    s = 0.5
    plt.scatter(x, position, s=s)
    plt.scatter(x, speed, s=s)

    plt.legend(['Position',  'Velocity'])
    plt.xlabel('Line')
    plt.ylabel('Position (mm) / Velocity (m/s^2)')
    plt.tight_layout()
    plt.show()
