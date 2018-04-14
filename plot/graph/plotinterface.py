from abc import ABCMeta, abstractmethod

class PlotInterface:
    __metaclass__ = ABCMeta

    @abstractmethod
    def plot(header, spot, gather):
        pass

    @abstractmethod
    def plotDirectory(subdirectory, save=False):
        pass
