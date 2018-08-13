import matplotlib.pyplot as plt

from common.data import *
from common.gauss import gaussfit
from common.util import get_vel_from_freq as vel
from plot.graph.plotinterface import PlotInterface

class SpeedRatioLoader(NPYLoader):

    @staticmethod
    def buildAndAppendData(id, header, spot, gather, run, data):
        ydatas = extractBrightestSpots(header, spot, gather, 30)
        f = header['LineFreq']

        deltax = []
        deltay = []
        for ydata in ydatas:
            params = gaussfit(ydata)
            deltax.append(params[3])
            deltay.append(params[4])

        if id not in data:
            data[id] = {
                'vel': [],
                'delta_x': [],
                'delta_y': [],
                'freq': [],
                'speed-diff': [],
                'speed-ratio': [],
                'error_x':[],
                'error_y':[]
            }

        data[id]['delta_x'].append(np.mean(deltax))
        data[id]['error_x'].append(np.std(deltax))

        data[id]['delta_y'].append(np.mean(deltay))
        data[id]['error_y'].append(np.std(deltay))

        data[id]['freq'].append(f)
        data[id]['vel'].append(run.vel)
        data[id]['speed-diff'].append(run.vel - vel(f))
        data[id]['speed-ratio'].append(round(run.vel / vel(f),4))

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

        f, ax = plt.subplots(len(data), sharex=True)
        plt.suptitle(r'Development of $\sigma_x$ and $\sigma_y$ of 2D-Gauss-Fit with changing speed-ratio')

        i = 0
        for id in data:

            values = data[id].tolist()
            label = str(int(values['freq'][0])) + " Hz"

            ax[i].scatter(values['speed-ratio'], values['delta_x'], label=label, alpha=.75, s=10)
            ax[i].legend(numpoints=1, loc='upper left')
            ax[i].grid()
            ax[i].set_ylim([1,10])
            ax[i].set_ylabel("$\sigma_x$")
            ax[i].errorbar(values['speed-ratio'], values['delta_x'], yerr=values['error_x'], linestyle="None")

            i += 1

        plt.show()
