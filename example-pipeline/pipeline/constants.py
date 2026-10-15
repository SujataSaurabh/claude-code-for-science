"""Pipeline constants.

All numeric constants used by the pipeline live here.
Never hardcode these values inline in other modules.
"""
from __future__ import annotations

RNG_SEED: int = 42
"""Seed for the NumPy default_rng used in generate_data; ensures reproducible tests."""

IMAGE_SIZE: tuple[int, int] = (256, 256)
"""Detector image dimensions (rows, cols) in pixels."""

CALIBRATION_SCALE: float = 0.95
"""Flat-field calibration scale factor applied to raw pixel intensities."""

RING_Q_VALUES: list[float] = [0.5, 1.0, 1.5]
"""Expected peak positions in q-space (Å⁻¹) for the synthetic ring pattern."""

RING_WIDTH: float = 0.03
"""Gaussian sigma (in q-units) of each synthetic ring peak."""

RING_AMPLITUDE: float = 500.0
"""Peak intensity of each synthetic ring before Poisson noise."""

DEAD_PIXELS: list[tuple[int, int]] = [(14, 23), (87, 102), (55, 201)]
"""List of (row, col) indices of known dead pixels.

Dead pixels are excluded from radial binning via a boolean mask.
They are never zeroed in the calibrated data array.
"""

N_RADIAL_BINS: int = 128
"""Number of radial bins for the azimuthal integration."""

Q_MAX: float = 2.0
"""Maximum q value (Å⁻¹) for the radial axis."""

PEAK_TOLERANCE_Q: float = 0.1
"""Maximum allowed q deviation (Å⁻¹) between a detected peak and a RING_Q_VALUE."""

SNR_FLOOR: float = 1.0
"""Minimum acceptable signal-to-noise ratio in the summary."""
