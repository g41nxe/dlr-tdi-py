from plot import helper
import numpy as np
import matplotlib.pyplot as plt

def plot(header, spot, gather):

    x, y = helper.align_data(header, spot, gather)

    max_pixel = np.argmax(y, 1)[np.argmax(np.max(y, 1))]

    f, ax = plt.subplots(1)
    plt.scatter(x, y[:, max_pixel], s=0.5)

    plt.title('PSF')
    plt.xlabel('Position (mm)')
    plt.ylabel('Intensity')

