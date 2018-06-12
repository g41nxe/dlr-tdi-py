import math
import matplotlib.pyplot as plt

from common.data import *
from common.gauss import gaussfit
from common.util import get_vel_from_freq as vel, fwhm
from plot.graph.plotinterface import PlotInterface

class SpeedRatioLoader(NPYLoader):

    @staticmethod
    def buildAndAppendData(id, header, spot, gather, run, data):
        ydata = extractBrightestSpot(header, spot, gather)
        f = header['LineFreq']

        params = gaussfit(ydata)

        if id not in data:
            data[id] = {
                'fwhm_x': [],
                'fwhm_y': [],
                'vel': [],
                'delta_x': [],
                'delta_y': [],
                'freq': [],
                'run': [],
                'speed-diff': [],
                'speed-ratio': [],
                'theta': [],
                'popt': [],
                'ydata': [],
                'cfg': []
            }

        data[id]['freq'].append(f)
        data[id]['ydata'].append(ydata)
        data[id]['cfg'].append(run)

        data[id]['popt'].append(params)
        data[id]['fwhm_x'].append(fwhm(params[3]))
        data[id]['fwhm_y'].append(fwhm(params[4]))
        data[id]['delta_x'].append(params[3])
        data[id]['delta_y'].append(params[4])
        data[id]['theta'].append(params[5])

        data[id]['vel'].append(run.vel)
        data[id]['run'].append(run.number)
        data[id]['speed-diff'].append(run.vel - vel(f))
        data[id]['speed-ratio'].append(round(vel(f) / run.vel, 2))

        return data

class SpeedRatioPlot(PlotInterface):

    @staticmethod
    def plot(header, spot, gather):
        pass

    @staticmethod
    def plotDirectory(subdirectory, save=False):
        loader = SpeedRatioLoader(subdirectory)
        data = loader.loadNPY()

        if save is True or len(data) < 1:
            loader.saveNPY()
            data = loader.loadNPY()

        f, ax = plt.subplots(3, sharex=True)
        plt.suptitle(r'Development of $\sigma_x$ and $\sigma_y$ of 2D-Gauss-Fit with changing speed-ratio')

        for i in [163216, 152841, 114324]:
            values = data[str(i)].tolist()
            label = str(int(values['vel'][0] / 0.00875)) + " Hz"

            ax[0].scatter(values['speed-ratio'], values['delta_x'], label=label, alpha=.75, s=10)
            ax[0].legend(numpoints=1, loc='upper left')
            ax[0].grid()
            ax[0].set_ylim([1, 10])
            ax[0].set_ylabel("$\sigma_x$")

            ax[1].scatter(values['speed-ratio'], values['delta_y'], label=label, alpha=.75, s=10)
            ax[1].legend(numpoints=1, loc='upper left')
            ax[1].grid()
            ax[1].set_ylim([1,10])
            ax[1].set_ylabel("$\sigma_y$")

            ax[2].scatter(values['speed-ratio'], values['theta'], label=label, alpha=.75, s=10)
            ax[2].legend(numpoints=1, loc='upper left')
            ax[2].grid()
            ax[2].set_ylim([-math.pi, math.pi])
            ax[2].set_ylabel(r"$\theta$")

            ax[2].set_xlabel("Speed ratio")

        plt.show()
