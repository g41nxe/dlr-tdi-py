from common.data import *
import numpy as np
import matplotlib.pyplot as plt
from plotinterface import PlotInterface

class PSFPlot(PlotInterface):
    @staticmethod
    def plot(header, spot, gather):

        x, y = buildCorrectedData(header, spot, gather)

        max_value_per_row       = np.max(y, 1)
        row_w_max_value         = np.argmax(max_value_per_row)
        px_w_max_value_per_row  = np.argmax(y, 1)

        max_px                  = px_w_max_value_per_row[row_w_max_value]

        plt.scatter(x , y[:, max_px], facecolors='none', edgecolors='b', s=12) #scatter psf

        plt.grid(linestyle='dotted', linewidth=1, color='gray')
        plt.xticks(np.arange(np.min(x), np.max(x), header['PixelSize']))

        plt.title('PSF')
        plt.ylabel('Intensity')
        plt.xlabel('Position (mm)')

