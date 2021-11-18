import numpy as np
from xhistogram.core import histogram


def cosd(theta):
    return np.cos(theta*np.pi/180)


def sind(theta):
    return np.sin(theta*np.pi/180)


def tand(theta):
    return np.tan(theta*np.pi/180)


def Vector_average(Direction, Norm, axis=-1):
    average = np.nanmean(Norm*np.exp(1j*Direction*np.pi/180), axis=axis)
    return np.angle(average)*180/np.pi, np.absolute(average)


def smallestSignedAngleBetween(x, y):
    """Calculate the smallest angle between two angle arrays.

    Parameters
    ----------
    x : array_like
        First angle.
    y : array_like
        Second angle.

    Returns
    -------
    array_like
        return the smallest angle between `y` and `x`, elementwise.

    """
    a = (x - y) % 360
    b = (y - x) % 360
    return np.where(a < b, -a, b)


def find_mode_distribution(data, bin_number):
    """Find de mode of a distribution from a serie of realisations of the random variable.

    Parameters
    ----------
    data : array_like
        serie of realisation of the random variable
    bin_number : int
        number of bins used is the calculation of the histogram.

    Returns
    -------
    float
        return the mode of the distribution.

    """
    counts, bins_edges = np.histogram(data, bins=bin_number)
    bin_centers = bins_edges[:-1] + (bins_edges[1] - bins_edges[0])
    return bin_centers[counts.argmax()]


def Make_angular_PDF(angles, weight, bin_edges=np.linspace(0, 360, 361), axis=-1):
    hist = histogram(angles, bins=bin_edges, density=1, weights=weight, axis=axis)
    bin_centers = bin_edges[1:] - (bin_edges[1] - bin_edges[0])/2
    return hist, bin_centers
