from common.data import *
import numpy as np
import matplotlib.pyplot as plt
import scipy as sp
import math
from plotinterface import PlotInterface

class MTFPlot(PlotInterface):

    @staticmethod
    def plot(header, spot, gather):

        x, y = buildCorrectedData(header, spot, gather)

        max_value_per_row       = np.max(y, 1)
        row_w_max_value         = np.argmax(max_value_per_row)
        px_w_max_value_per_row  = np.argmax(y, 1)
        max_px                  = px_w_max_value_per_row[row_w_max_value]

        x = x - x[np.argmax(y[:, max_px])] # peak at 0
        y = y[:, max_px]

        xy = np.array([np.sort(x), y[np.argsort(x)]]) # sort by x (position)

        psf = np.array(xy[1,:])
        otf = np.fft.rfft(psf)
        mtf = np.absolute(otf)
        mtf = (mtf - np.min(mtf)) / (np.max(mtf) - np.min(mtf))

        f, (ax1, ax2) = plt.subplots(2)

        ax1.scatter(xy[0,:], xy[1,:], facecolors='none', edgecolors='b', s=12)
        ax1.grid(linestyle='dotted', linewidth=1, color='gray')
        ax1.set_xlim(-0.1, 0.1)
        ax1.set_xticks(np.arange(-0.1, 0.1, header['PixelSize']))
        ax1.set_xticklabels(np.round(np.arange(-0.1, 0.1, header['PixelSize'])/header['PixelSize']), rotation=45, size=9)

        ax1.set_title('PSF')
        ax1.set_ylabel('Intensity [DN]')
        ax1.set_xlabel('Position [mm]')

        ax2.scatter(np.arange(0, len(mtf)), mtf, facecolors='none', edgecolors='b', s=12)

        ax2.grid(linestyle='dotted', linewidth=1, color='gray')
        ax2.set_title('MTF')
        ax2.set_ylabel('MTF [a.u.]')
        ax2.set_xlim(0, 1000)
        ax2.set_xlabel('Ortsfrequenz [cy/mm]')

        plt.tight_layout()

