from abc import ABCMeta, abstractmethod

class AnimationInterface:
    __metaclass__ = ABCMeta


    @abstractmethod
    def plot(header, spot, gather):
        pass

    @abstractmethod
    def plotDirectory(subdirectory, save=False):
        pass
