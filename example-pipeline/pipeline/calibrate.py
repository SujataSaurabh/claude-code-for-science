"""Detector calibration: flat-field correction and dead-pixel masking.

Dead pixels are represented as a boolean mask (True = valid, False = dead).
They are *excluded* from downstream computation, never zeroed in the data array.
"""
from __future__ import annotations

import logging

import numpy as np

from pipeline.constants import CALIBRATION_SCALE, DEAD_PIXELS

log = logging.getLogger(__name__)


def make_mask(shape: tuple[int, int]) -> np.ndarray:
    """Build the boolean valid-pixel mask for a given detector shape.

    Parameters
    ----------
    shape : tuple[int, int]
        Detector dimensions (rows, cols).

    Returns
    -------
    np.ndarray
        Boolean mask, shape (rows, cols). True = valid pixel, False = dead.
    """
    mask = np.ones(shape, dtype=bool)
    for row, col in DEAD_PIXELS:
        if 0 <= row < shape[0] and 0 <= col < shape[1]:
            mask[row, col] = False
        else:
            log.warning(
                "Dead pixel (%d, %d) is outside image shape %s; ignoring",
                row,
                col,
                shape,
            )
    n_dead = mask.size - mask.sum()
    log.debug("Mask built: %d dead pixels out of %d total", n_dead, mask.size)
    return mask


def calibrate(
    image: np.ndarray,
    scale: float = CALIBRATION_SCALE,
    mask: np.ndarray | None = None,
) -> tuple[np.ndarray, np.ndarray]:
    """Apply flat-field calibration and return the corrected image with its pixel mask.

    Dead pixels are flagged in the mask but the calibrated image values at those
    positions are left as-is; downstream stages must respect the mask.

    Parameters
    ----------
    image : np.ndarray
        Raw detector image, shape (H, W), dtype float64.
    scale : float
        Flat-field scale factor applied element-wise to every pixel.
    mask : np.ndarray or None
        Pre-computed boolean mask, shape (H, W). If None, ``make_mask`` is called
        with ``image.shape``.

    Returns
    -------
    calibrated : np.ndarray
        Flat-field corrected image, same shape and dtype as ``image``.
    mask : np.ndarray
        Boolean valid-pixel mask, same shape as ``image``.

    Raises
    ------
    ValueError
        If a provided ``mask`` shape does not match ``image`` shape.

    Examples
    --------
    >>> import numpy as np
    >>> img = np.ones((256, 256))
    >>> cal, msk = calibrate(img)
    >>> cal[0, 0]
    0.95
    """
    if mask is None:
        mask = make_mask(image.shape)
    elif mask.shape != image.shape:
        raise ValueError(
            f"mask shape {mask.shape} does not match image shape {image.shape}"
        )

    log.info("Calibrating image shape=%s with scale=%.4f", image.shape, scale)
    calibrated = image * scale
    log.info("Calibration complete; %d pixels excluded by mask", (~mask).sum())
    return calibrated, mask
