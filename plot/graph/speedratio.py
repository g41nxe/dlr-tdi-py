import matplotlib.pyplot as plt

from common.data import *
from common.gauss import gaussfit
from common.util import get_vel_from_freq as vel
from plot.graph.plotinterface import PlotInterface

class SpeedRatioLoader(NPYLoader):

    @staticmethod
    def buildAndAppendData(id, header, spot, gather, run, data):
        ydatas, px = extractBrightestSpots(header, spot, gather)
        f = header['LineFreq']
        p = header['FirstPixel'] + px

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
                'error_x': [],
                'error_y': []
            }

        data[id]['delta_x'].append(np.mean(deltax))
        data[id]['error_x'].append(np.std(deltax))

        data[id]['delta_y'].append(np.mean(deltay))
        data[id]['error_y'].append(np.std(deltay))

        data[id]['freq'].append(f)
        data[id]['vel'].append(run.vel)
        data[id]['speed-diff'].append(run.vel - vel(f))
        data[id]['speed-ratio'].append(round(run.vel / vel(f), 4))
        data[id]['Pixel'] = p

        return data


class SpeedRatioPlot(PlotInterface):
    colors = [
        '#d73027',
        '#fc8d59',
        '#4575b4',
        '#fee090',
        '#91bfdb',
    ]

    marker = [
        "o",
        "v",
        "*",
        "s",
        "d",
        "x"
    ]

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

        f, ax = plt.subplots(2, sharex=True)
        #plt.suptitle(r'Development of $\sigma_x$ and $\sigma_y$ of 2D-Gauss-Fit with changing speed-ratio')

        frequencies = {}
        for id, array in data.items():
            freq = array.tolist()['freq'][0]
            frequencies[freq] = id

        c_id = 0
        for f in sorted(frequencies):
            values = data[frequencies[f]].tolist()

            label = str(int(values['freq'][0])) + " Hz"

            ax[0].errorbar(values['speed-ratio'], values['delta_x'], yerr=values['error_x'],
                           c=SpeedRatioPlot.colors[c_id], linestyle="None", alpha=.75)

            ax[0].plot(values['speed-ratio'], values['delta_x'], SpeedRatioPlot.marker[c_id] + '-',
                       label=label, markersize=4, alpha=.75, linewidth=1, c=SpeedRatioPlot.colors[c_id])

            ax[0].legend(numpoints=1, loc='upper right')
            ax[0].grid()
            ax[0].set_ylim([1, 16])
            ax[0].set_ylabel("$\sigma_x$ [u.a.]")

            ax[1].errorbar(values['speed-ratio'], values['delta_y'], yerr=values['error_y'],
                           c=SpeedRatioPlot.colors[c_id], linestyle="None", alpha=.75)

            ax[1].plot(values['speed-ratio'], values['delta_y'], SpeedRatioPlot.marker[c_id] + '-',
                       label=label, markersize=4, alpha=.75, linewidth=1, c=SpeedRatioPlot.colors[c_id])

            ax[1].legend(numpoints=1, loc='upper right')
            ax[1].grid()
            ax[1].set_ylim([1, 16])
            ax[1].set_ylabel("$\sigma_y$ [u.a.]")

            ax[1].set_xlabel("Speed-Ratio $v_{fps} \;/\; v_{tdi}$ [u.a.]")

            c_id += 1

        ax[0].text(1, 1.1, 'Pixel: ' + str(values['Pixel']), transform=ax[0].transAxes, fontsize=8, horizontalalignment='right', verticalalignment='top')

        plt.show()
