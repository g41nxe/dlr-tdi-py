import matplotlib.pyplot as plt
from plot.graph.plotinterface import PlotInterface

class GatheringPlot(PlotInterface):

    @staticmethod
    def plot(header, spot, gather):

        position = gather[:, 0]
        speed    = gather[:, 1]
        x        = range(0, len(position))

        # Two subplots, the axes array is 1-d

        s = 0.5
        f, (ax1, ax2) = plt.subplots(2, sharex=True)

        ax1.scatter(x, position, s=s)
        ax1.set_ylabel('Line')
        ax1.set_ylabel('Position (mm)')
        ax1.set_title('Position and Velocity')

        ax2.scatter(x, speed, s=s)
        ax2.set_ylabel('Velocity (mm/s)')

        plt.setp(ax2.get_xticklabels(), fontsize=6)
        plt.setp(ax1.get_xticklabels(), visible=False)
        plt.tight_layout()
