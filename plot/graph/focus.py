import matplotlib.pyplot as plt

from common.data import *
from common.gauss import gaussfit
from plot.graph.plotinterface import PlotInterface

class SpeedRatioLoader(NPYLoader):

    @staticmethod
    def buildAndAppendData(id, header, spot, gather, run, data):
        ydata = extractBrightestSpot(header, spot, gather)

        params = gaussfit(ydata)

        if id not in data:
            data[id] = {
                'position': [],
                'delta_x': [],
                'delta_y': [],
            }

        position = None
        for (name, pos) in run.pos:
            if name is Config.get("CAM_Y_GROUP"):
                position = pos[0]
                break

        if position is None:
            raise ValueError("No position value in task file!")

        data[id]['position'].append(position)
        data[id]['delta_x'].append(params[3])
        data[id]['delta_y'].append(params[4])
        return data

class SpeedRatioPlot(PlotInterface):

    @staticmethod
    def plotDirectory(header, spot, gather):
        pass

    @staticmethod
    def plot(subdirectory, save=False):
        loader = SpeedRatioLoader(subdirectory)
        data = loader.loadNPY()

        if save is True or len(data) < 1:
            loader.saveNPY()
            data = loader.loadNPY()

        f, ax = plt.subplots(2, sharex=True)
        plt.suptitle(r'Development of $\sigma_x$ and $\sigma_y$ of 2D-Gauss-Fit with changing Position')

        for i in data:
            values = data[str(i)].tolist()

            ax[0].scatter(values['position'], values['delta_x'], )
            ax[1].scatter(values['position'], values['delta_y'], )

            ax[0].set_ylabel("$\sigma_x$")
            ax[1].set_ylabel("$\sigma_x$")

        plt.show()
