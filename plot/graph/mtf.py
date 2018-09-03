#!/usr/bin/env python
# -*- coding: utf-8 -*-

from common.data import *
import numpy as np
import matplotlib.pyplot as plt
from common.gauss import gaussfit2, gauss

from plot.graph.plotinterface import PlotInterface


class MTFPlot(PlotInterface):
    colors = [
        '#fc8d59',
        '#d73027',
        '#4575b4',
    ]

    marker = [
        "o",
        "x"
    ]

    @staticmethod
    def plot(header, spot, gather):
        x, y = buildCorrectedData(header, spot, gather)

        max_value_per_row = np.max(y, 1)
        row_w_max_value = np.argmax(max_value_per_row)
        px_w_max_value_per_row = np.argmax(y, 1)
        max_px = px_w_max_value_per_row[row_w_max_value]

        x = x - x[np.argmax(y[:, max_px])]  # peak at 0
        y = y[:, max_px]

        xy = np.array([np.sort(x), y[np.argsort(x)]])  # sort by x (position)

        xp = np.linspace(-0.1, 0.1, 100)
        yp = np.interp(xp, xy[0, :], xy[1, :])

        psf = yp  # np.array(xy[1, :])
        otf = np.fft.rfft(psf)
        mtf = np.absolute(otf)
        mtf = (mtf - np.min(mtf)) / (np.max(mtf) - np.min(mtf))

        px = max_px + header['FirstPixel']

        xticks = np.arange(0, len(mtf)) * (header['PixelSize'] * 10)

        p = gaussfit2(xy[1, :], xy[0, :])
        fwhm = 2 * np.sqrt(2 * np.log(2)) * p[1]
        x_fitted = np.linspace(-0.1, 0.1, 100)
        y_fitted = gauss(x_fitted, *p)

        otf_fitted = np.fft.rfft(y_fitted)
        mtf_fitted = np.absolute(otf_fitted)
        mtf_fitted = (mtf_fitted - np.min(mtf_fitted)) / (np.max(mtf_fitted) - np.min(mtf_fitted))

        xticks_fitted = np.arange(0, len(mtf_fitted)) * (header['PixelSize'] * 10)

        f, (ax1, ax2) = plt.subplots(2)

        ax1.axvspan(x_fitted[np.argmax(y_fitted)] - fwhm / 2, x_fitted[np.argmax(y_fitted)] + fwhm / 2, alpha=0.3,
                    color='gray', zorder=0)
        ax1.annotate(s='', xy=(x_fitted[np.argmax(y_fitted)] - fwhm / 2, 300),
                     xytext=(x_fitted[np.argmax(y_fitted)] + fwhm / 2, 300), arrowprops=dict(arrowstyle='<->'))
        ax1.annotate(s='FWHM: ' + str(round(fwhm / header['PixelSize'], 2)), xy=(x_fitted[np.argmax(y_fitted)], 350),
                     horizontalalignment='center')

        ax1.scatter(xy[0, :], xy[1, :], facecolors=MTFPlot.colors[0], edgecolors=MTFPlot.colors[0], s=14,
                    marker=MTFPlot.marker[0], label='Messdaten')
        ax1.scatter(xp, yp, facecolors=MTFPlot.colors[1], edgecolors=MTFPlot.colors[1], s=14, marker=MTFPlot.marker[1],
                    label='lin. interpoliert')
        ax1.plot(x_fitted, y_fitted, c=MTFPlot.colors[2], label=u'Gauß-Fit')


        xx = np.arange(0-header['PixelSize']/2, -0.1, -header['PixelSize'])[::-1]
        xx = np.append(xx, np.arange(0+header['PixelSize']/2,0.1, header['PixelSize']))
        ax1.set_xticks(xx)

        ax1.grid(linestyle='dotted', linewidth=1, color='gray')
        ax1.set_xlim(-0.1, 0.1)
        ax1.tick_params(axis='both', which='major', length=1.5, right=True, top=True)
        ax1.tick_params(axis='both', which='minor', length=1.5, color='white')


        xx = np.arange(0, -0.1, -header['PixelSize'])[::-1]
        xx = np.append(xx, np.arange(header['PixelSize'],0.1, header['PixelSize']))
        ax1.set_xticks(xx, minor=True)

        ax1.set_xticklabels([])
        ax1.set_xticklabels(np.around(xx / header['PixelSize']).astype(int), size=7, minor=True)

        ax1.set_title('PSF')
        ax1.set_ylabel(u'Intensität [DN]')
        ax1.set_xlabel('Position [px]')
        ax1.legend(numpoints=1, loc='upper right')

        width = 0.01
        ax2.bar(xticks - (width / 2), mtf, color=MTFPlot.colors[1], width=width, align='center',
                label='lin. interpoliert')
        ax2.bar(xticks_fitted + (width / 2), mtf_fitted, color=MTFPlot.colors[2], width=width, align='center',
                label=u'Gauß-Fit')

        ax2.grid(linestyle='dotted', linewidth=1, color='gray')
        plt.xticks(np.round(xticks, 2), fontsize=7)
        ax2.set_title('MTF')
        ax2.set_ylabel('MTF [a.u.]')
        ax2.set_xlim(-0.03, 1.03)
        ax2.set_xlabel('Ortsfrequenz [cy/px]')
        ax2.legend(numpoints=1, loc='upper right')

        ax1.text(1, 1.1, 'Pixel: ' + str(px), transform=ax1.transAxes, fontsize=8, horizontalalignment='right',
                 verticalalignment='top')

        plt.tight_layout()
