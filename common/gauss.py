import math
import numpy as np

from scipy.optimize import curve_fit

def gauss2d(xy, A, x0, y0, sigma_x, sigma_y, theta):
    (x, y) = xy

    a =  math.cos(  theta)**2 / (2 * sigma_x ** 2) + math.sin(  theta)**2 / (2*sigma_y**2)
    b = -math.sin(2*theta)    / (4 * sigma_x ** 2) + math.sin(2*theta)    / (4*sigma_y**2)
    c =  math.sin(  theta)**2 / (2 * sigma_x ** 2) + math.cos(  theta)**2 / (2*sigma_y**2)

    g =  A * np.exp( - (a*(x-x0)**2 + 2*b*(x-x0)*(y-y0) + c*(y-y0)**2))

    return g.ravel()

def initial(data):

    cx, cy  = np.unravel_index(data.argmax(), data.shape)
    A       = data[cx, cy]
    sigma_x = np.sqrt(data[cx, :].std())
    sigma_y = np.sqrt(data[:, cy].std())

    total = data.sum()

    X, Y = np.indices(data.shape)

    Mxx = np.ma.sum((X - cx) * (X - cx) * data) / total
    Myy = np.ma.sum((Y - cy) * (Y - cy) * data) / total
    Mxy = np.ma.sum((X - cx) * (Y - cy) * data) / total

    rot = 0.5 * np.arctan(2 * Mxy / (Mxx - Myy))

    return A, cx, cy, sigma_x, sigma_y, rot

def gaussfit(ydata):
    pixelCount = ydata.shape[0]

    x, y  = np.meshgrid(np.linspace(1, pixelCount, pixelCount), np.linspace(1, pixelCount, pixelCount))

    popt, pcov = curve_fit(gauss2d, (x, y), ydata.ravel(),
                           p0=initial(ydata),
                           bounds=([0, 0, 0, 0, 0, -math.pi], [5000, 32, 32, np.inf, np.inf, math.pi]))
    return popt