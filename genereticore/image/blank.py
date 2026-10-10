"""Conservative cleared-canvas detection before guides or inversion."""
import numpy as np


def is_blank(picture):
    pixels = np.asarray(picture.convert('RGB'), dtype=np.int16)
    # Every pixel must be nearly the same color. Even a small dark stroke
    # prevents the alternate prompt; no downsampling can miss thin marks.
    return bool(np.max(np.ptp(pixels, axis=(0, 1))) <= 3)
