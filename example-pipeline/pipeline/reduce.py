"""Azimuthal integration: 2D detector image → 1D I(q) curve.

Dead pixels (mask == False) are excluded from every radial bin.
No pyFAI dependency; uses pure NumPy binning.
"""
from __future__ import annotations

import logging

import numpy as np

from pipeline.constants import N_RADIAL_BINS, Q_MAX

log = logging.getLogger(__name__)


def _radial_q_map(shape: tuple[int, int], q_max: float) -> np.ndarray:
    """Compute radial q-coordinate for each pixel.

    Parameters
    ----------
    shape : tuple[int, int]
        Image dimensions (rows, cols).
    q_max : float
        Maximum q value at the image corner (Å⁻¹).

    Returns
    -------
    np.ndarray
        2D array of q values, shape (rows, cols).
    """
    rows, cols = shape
    cy, cx = rows / 2.0, cols / 2.0
    y = np.arange(rows) - cy
    x = np.arange(cols) - cx
    xx, yy = np.meshgrid(x, y)
    r = np.sqrt(xx**2 + yy**2)
    r_max = np.sqrt(cx**2 + cy**2)
    return (r / r_max) * q_max


def reduce(
    image: np.ndarray,
    mask: np.ndarray,
    n_bins: int = N_RADIAL_BINS,
    q_max: float = Q_MAX,
) -> tuple[np.ndarray, np.ndarray]:
    """Azimuthal integration using radial binning.

    Each radial bin accumulates only the valid pixels (where ``mask`` is True).
    Bins with no valid pixels receive intensity 0.0.

    Parameters
    ----------
    image : np.ndarray
        Calibrated 2D detector image, shape (H, W).
    mask : np.ndarray
        Boolean valid-pixel mask, shape (H, W). True = include in binning.
    n_bins : int
        Number of radial bins in the output.
    q_max : float
        Maximum q value (Å⁻¹) for the radial axis.

    Returns
    -------
    q_arr : np.ndarray
        Bin-centre q values, shape (n_bins,).
    I_arr : np.ndarray
        Azimuthally averaged intensity per bin, shape (n_bins,).

    Raises
    ------
    ValueError
        If ``image`` and ``mask`` shapes do not match.

    Examples
    --------
    >>> import numpy as np
    >>> img = np.ones((256, 256))
    >>> msk = np.ones((256, 256), dtype=bool)
    >>> q, I = reduce(img, msk)
    >>> q.shape
    (128,)
    """
    if image.shape != mask.shape:
        raise ValueError(
            f"image shape {image.shape} does not match mask shape {mask.shape}"
        )

    log.info(
        "Reducing image shape=%s with %d valid pixels into %d bins",
        image.shape,
        mask.sum(),
        n_bins,
    )

    q_map = _radial_q_map(image.shape, q_max)
    bin_edges = np.linspace(0.0, q_max, n_bins + 1)
    q_arr = 0.5 * (bin_edges[:-1] + bin_edges[1:])

    # Flatten and apply mask before binning
    q_flat = q_map[mask]
    I_flat = image[mask]

    bin_indices = np.digitize(q_flat, bin_edges) - 1
    bin_indices = np.clip(bin_indices, 0, n_bins - 1)

    I_arr = np.zeros(n_bins, dtype=np.float64)
    counts = np.zeros(n_bins, dtype=np.int64)

    np.add.at(I_arr, bin_indices, I_flat)
    np.add.at(counts, bin_indices, 1)

    nonzero = counts > 0
    I_arr[nonzero] /= counts[nonzero]

    n_empty = int((counts == 0).sum())
    if n_empty:
        log.warning("%d radial bins have no valid pixels", n_empty)

    peak_idx = int(I_arr.argmax())
    log.info(
        "Reduction complete; peak I=%.2f at q=%.3f",
        I_arr[peak_idx],
        q_arr[peak_idx],
    )
    return q_arr, I_arr
