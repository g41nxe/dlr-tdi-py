import matplotlib.pyplot as plt
from common.config import Config
from common.peaks import detect_peaks
from common.data import buildCorrectedData
import numpy as np

from plot.graph.plotinterface import PlotInterface

class SpotPlot(PlotInterface):
    @staticmethod
    def plot(header, spot, gather):


        x,y = buildCorrectedData(header, spot, gather)

        line, col = np.unravel_index(y.argmax(), y.shape)

        pixelCount = header['PixelCount']

        fig, ax = plt.subplots(pixelCount, sharex=True)

        fig.suptitle('Intensities of all Pixels')

        for i in range(0, pixelCount):
            data = y[:, i]

            if i == col:
                tops = detect_peaks(data, mph=data.max() * 0.75, mpd=200, edge='rising')
                ax[i].plot(tops, data[tops], 'o', c='red', markersize=3)


            ax[i].plot(data)
            ax[i].set_ylim(0, y.max())
            ax[i].set_ylabel(i,  fontsize=5)
            ax[i].set_yticklabels([])

        plt.tick_params(axis='both', which='major', labelsize=5)
        fig.text(0.5, 0.04, 'Line', ha='center')
        fig.text(0.04, 0.5, 'Pixel', va='center', rotation='vertical')
        fig.text(0.1, 0.04, 'max: ' + str(y.max()) + ' count: ' + str(len(tops)), ha='center', size=8)


