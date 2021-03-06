# -*- coding: utf-8 -*-
"""
Created on Fri Mar  5 12:31:12 2021

@author: kirstenl
"""

import cv2
import pywt
import numpy as np
import matplotlib.pyplot as plt
from numba import njit
from .wavelets import dwt2, idwt2


@njit()
def _remove_low_values(x, alpha):
    """
    Remove low values for array.

    """
    
    # flatten x and store shape
    shape = x.shape
    x = x.reshape(-1)

    nonzero = float(np.count_nonzero(x))
    lenx = float(len(x))
    
    # iterate over sorted values and indexes of |x| to eliminate low values
    for i, xx in zip(np.argsort(np.abs(x)), np.sort(np.abs(x))):
        # verify if the ratio is as expected
        if (nonzero / lenx) <= alpha:
            break

        # if not already zero, set to zero
        if xx != 0:
            x[i] = 0
            nonzero -= 1

    # reshape to original shape and return
    return x.reshape(*shape)


def compact_image(x, alpha, wavelet='haar', J=1):
    """
    Compact 2D input image using Wavelet Transform.

    Parameters
    ----------
    x : numpy.ndarray
        Input signal.
    alpha : float ranging from (0, 1]
        Percentage of high gradients to mantain from detail coefficients.
    wavelet : str or list<numpy.ndarray>, optional
        Wavelet filter to be used. The default is haar.
    J : int, optional
        Maximum decomposition level. The default is 1.

    Returns
    -------
    [cA] : list<numpy.ndarray>
        Intermidiate smooth signals.
    Dj : list<numpy.ndarray>
        Detail coefficients.
    cA : numpy.ndarray
        Final compatc signal.

    """
    assert J > 0, 'J should be greater than 0!'
    assert 0 < alpha <= 1, 'alpha should be between [0,1]!'

    # going forward in the wavelet transform
    Dj = []
    cA = np.copy(x)
    for j in range(J):
        cA, cD = dwt2(cA, wavelet=wavelet)

        # remove low values
        Dj.append([_remove_low_values(d, alpha) for d in cD])

    # store values to be returned
    returns = (cA, Dj)

    # returning to the compacted image
    for j, dj in enumerate(reversed(Dj)):
        cA = idwt2(cA, dj, wavelet=wavelet)
    cA = cA.astype(x.dtype)
        
    return returns + (cA,)


if __name__ == '__main__':
    # number of iterations
    J = 3

    # parameter for compacting
    alpha = 0.1

    # define input image
    x = cv2.imread('./barbara.jpg')
    x = cv2.cvtColor(x, cv2.COLOR_BGR2GRAY)

    # compact image
    (cA, Dj, reconstructed) = compact_image(x, J=J, alpha=alpha)

    fig, axs = plt.subplots(1, 2)
    fig.suptitle(f'Own: Compacted image J={J}')
    axs[0].imshow(x)
    axs[0].set_title('Original image')

    axs[1].imshow(reconstructed)
    axs[1].set_title('Reconstructed image')