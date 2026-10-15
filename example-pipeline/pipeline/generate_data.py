"""Synthetic 2D detector image generation.

Produces a ring pattern similar to what a powder diffraction beamline detector
would record, with configurable q-positions, Gaussian ring widths, and Poisson noise.
All parameters come from constants.py; no real data is used.
"""
from __future__ import annotations

import logging

import numpy as np

from pipeline.constants import (
    IMAGE_SIZE,
    Q_MAX,
    RING_AMPLITUDE,
    RING_Q_VALUES,
    RING_WIDTH,
    RNG_SEED,
)

log = logging.getLogger(__name__)


def _radial_q_map(shape: tuple[int, int], q_max: float) -> np.ndarray:
    """Compute radial q-coordinate for each pixel.

    Parameters
    ----------
    shape : tuple[int, int]
        Image dimensions (rows, cols).
    q_max : float
        Maximum q value mapped to the image edge (Å⁻¹).

    Returns
    -------
    np.ndarray
        2D array of q-values, shape matching ``shape``.
    """
    rows, cols = shape
    cy, cx = rows / 2.0, cols / 2.0
    y = np.arange(rows) - cy
    x = np.arange(cols) - cx
    xx, yy = np.meshgrid(x, y)
    r = np.sqrt(xx**2 + yy**2)
    r_max = np.sqrt(cx**2 + cy**2)
    return (r / r_max) * q_max


def generate_data(
    shape: tuple[int, int] = IMAGE_SIZE,
    q_values: list[float] | None = None,
    ring_width: float = RING_WIDTH,
    amplitude: float = RING_AMPLITUDE,
    q_max: float = Q_MAX,
    seed: int = RNG_SEED,
) -> tuple[np.ndarray, dict[str, object]]:
    """Generate a synthetic 2D detector image with ring patterns.

    Creates Gaussian rings at the specified q-positions and adds Poisson noise.
    The image simulates powder diffraction data without any real measurements.

    Parameters
    ----------
    shape : tuple[int, int]
        Detector dimensions (rows, cols) in pixels.
    q_values : list[float] or None
        Peak positions in q-space (Å⁻¹). Defaults to ``RING_Q_VALUES``.
    ring_width : float
        Gaussian sigma of each ring peak (Å⁻¹).
    amplitude : float
        Peak intensity before Poisson noise.
    q_max : float
        Maximum q value mapped to the image edge (Å⁻¹).
    seed : int
        RNG seed for reproducible noise.

    Returns
    -------
    image : np.ndarray
        Synthetic detector image, shape (rows, cols), dtype float64.
    metadata : dict[str, object]
        Provenance information: shape, q_values, seed, q_max.

    Examples
    --------
    >>> image, meta = generate_data()
    >>> image.shape
    (256, 256)
    >>> image.min() >= 0
    True
    """
    if q_values is None:
        q_values = RING_Q_VALUES

    log.info(
        "Generating synthetic detector image: shape=%s, %d rings, seed=%d",
        shape,
        len(q_values),
        seed,
    )

    q_map = _radial_q_map(shape, q_max)
    signal = np.zeros(shape, dtype=np.float64)

    for q0 in q_values:
        ring = amplitude * np.exp(-0.5 * ((q_map - q0) / ring_width) ** 2)
        signal += ring
        log.debug("Added ring at q=%.3f Å⁻¹", q0)

    rng = np.random.default_rng(seed)
    image = rng.poisson(np.clip(signal, 0, None)).astype(np.float64)

    metadata: dict[str, object] = {
        "shape": shape,
        "q_values": q_values,
        "seed": seed,
        "q_max": q_max,
        "ring_width": ring_width,
        "amplitude": amplitude,
    }
    log.info("Image generated; total counts: %.1f", image.sum())
    return image, metadata
