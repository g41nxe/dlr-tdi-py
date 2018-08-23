import os, shutil
import matplotlib.cm as cm
import matplotlib.colors as colors
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

from mpl_toolkits.axes_grid1.inset_locator import inset_axes
from plot.animation.animationinterface import AnimationInterface

from common.data import *
from common.data import NPYLoader
from common.gauss import gaussfit

framedata = []    # data values to plot for the current frame
ax        = None  # axis object
cb        = None  # colorbar object
ymin      = 0     # global min
ymax      = 0     # global max

class SpotVideoLoader(NPYLoader):

    @staticmethod
    def buildAndAppendData(id, header, spot, gather, run, data):
        ydata = extractBrightestSpots(header, spot, gather, 5)[4]
        popt = gaussfit(ydata)

        if id not in data.keys():
            data[id] = {}

        data[id][run.number] = {}
        data[id][run.number]['popt'] = popt
        data[id][run.number]['ydata'] = ydata

        return data

class SpotVideoPlot(AnimationInterface):

    @staticmethod
    def plot(header, spot, gather):
        pass

    @staticmethod
    def plotDirectory(subdirectory, save=False):
        global ax, ymin, ymax, framedata

        framedata = []

        loader = SpotVideoLoader(subdirectory)
        gauss = loader.loadNPY()

        if save is True or len(gauss) < 1:
            loader.saveNPY()
            gauss = loader.loadNPY()

        for id in gauss.keys():
            pixelCount = ymin = ymax = 0

            data = (gauss[id]).tolist()

            for run in sorted(data, key=int):
                values = data[run]
                ymax = max(ymax, np.max(values['ydata']))
                ymin = min(ymin, np.min(values['ydata']))
                pixelCount = max(pixelCount, values['ydata'].shape[0])

                framedata.append({'ydata': values['ydata'], 'popt': values['popt'], 'run': run})

            f, ax = SpotVideoPlot.style(pixelCount)

            #anim = FuncAnimation(f, SpotVideoPlot.frame, frames=np.arange(0, len(framedata)), interval=200)

            if os.path.exists(subdirectory + "\\video-" + id):
                shutil.rmtree(subdirectory + "\\video-" + id)

            os.makedirs(subdirectory + "\\video-" + id)

            for i, val in enumerate(framedata):
                SpotVideoPlot.frame(i)
                f.savefig(subdirectory + "\\video-" + id + "\\speed-ratio-" + str(i) + ".jpg", bbox_inches='tight')

            #anim.save(filename=subdirectory + "\\" + id + ".mp4", dpi=80, writer='ffmpeg')

    @staticmethod
    def style(pixelCount):
        f, axis = plt.subplots(1)

        axis.grid(linestyle='dashed', alpha=.3)

        axis.set_xticks(np.arange(0.5, pixelCount, 1))
        axis.set_yticks(np.arange(0.5, pixelCount, 1))

        axis.set_xticklabels('')
        axis.set_yticklabels('')

        axis.set_xticks(np.arange(0, pixelCount, 5), minor=True)
        axis.set_xticklabels(np.arange(0, pixelCount, 5), minor=True)

        axis.set_yticks(np.arange(0, pixelCount, 5), minor=True)
        axis.set_yticklabels(np.arange(0, pixelCount, 5), minor=True)

        axis.tick_params(axis='both', which='major', length=1.5, right=True, top=True)
        axis.tick_params(axis='both', which='minor', length=1.5, color='white')

        plt.setp([
            axis.get_yminorticklabels(), axis.get_xminorticklabels(),
        ], fontsize=6, linespacing=1)

        axis.set_xlim(-0.5, pixelCount - 0.5)
        axis.set_ylim(-0.5, pixelCount - 0.5)

        #plt.suptitle('Spot-Image with 2D-Gaussian Fit')

        return f, axis

    @staticmethod
    def colorbar(ax, p):
        cax = inset_axes(ax, width="95%", height="3%", loc=9)

        c = plt.colorbar(p, cax=cax, orientation="horizontal")

        c.ax.tick_params(labelsize=6, color='#cccccc')
        c.outline.set_edgecolor('#cccccc')

        cxtick = plt.getp(c.ax.axes, 'yticklabels')
        cytick = plt.getp(c.ax.axes, 'xticklabels')
        plt.setp([cxtick, cytick], color='#cccccc', fontsize=0)

        return c

    @staticmethod
    def frame(i):
        global framedata

        SpotVideoPlot.update(framedata[i]['ydata'], framedata[i]['popt'], framedata[i]['run'])

    @staticmethod
    def update(ydata, popt, id):
        global cb, ymin, ymax, ax

        norm = colors.Normalize(vmin=ymin, vmax=ymax)
        p = ax.imshow(ydata, cmap=cm.gray, origin="bottom", norm=norm)

        if not cb is None:
            cb.remove()

        cb = SpotVideoPlot.colorbar(ax, p)

        ax.set_title("Run " + str(id), loc='center', fontsize=20)
        return
