from common.io import *
import numpy as np
import matplotlib.pyplot as plt
import scipy as sp
import math
def plot(header, spot, gather):

    x, y = buildCorrectedData(header, spot, gather)

    max_value_per_row       = np.max(y, 1)
    row_w_max_value         = np.argmax(max_value_per_row)
    px_w_max_value_per_row  = np.argmax(y, 1)
    max_px                  = px_w_max_value_per_row[row_w_max_value]
    x                       = x - x[np.argmax(y[:, max_px])]

    y = y[:, max_px]

    xy = np.array([np.sort(x), y[np.argsort(x)]]) # sort by x (position)

    psf = np.array(xy[1,:])
    otf = np.fft.rfft(psf)
    mtf = np.absolute(otf)
    mtf = (mtf - np.min(mtf)) / (np.max(mtf) - np.min(mtf))

    #freq = np.fft.fftfreq(psf.size, 1./8.75)
    #plot.scatter(freq,mtf)
    #plt.plot(mtf)
    plt.plot(mtf)

    plt.grid(linestyle='dotted', linewidth=1, color='gray')


    plt.title('MTF')
    plt.ylabel('MTF [a.u.]')
    plt.xlabel('Ortsfrequenz [cy/um]')

def Ai(x):
    (ai, ai_prime, bi, bi_prime) = sp.special.airy(x)
    return bi

