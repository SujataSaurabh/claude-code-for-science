"""Tests for reduce.py."""
from __future__ import annotations

import numpy as np
import pytest

from pipeline.calibrate import calibrate
from pipeline.constants import N_RADIAL_BINS, PEAK_TOLERANCE_Q, RING_Q_VALUES
from pipeline.generate_data import generate_data
from pipeline.reduce import reduce


def test_output_shapes() -> None:
    image = np.ones((64, 64))
    mask = np.ones((64, 64), dtype=bool)
    q, intensity = reduce(image, mask, n_bins=64)
    assert q.shape == (64,)
    assert intensity.shape == (64,)


def test_default_n_bins() -> None:
    image = np.ones((64, 64))
    mask = np.ones((64, 64), dtype=bool)
    q, intensity = reduce(image, mask)
    assert len(q) == N_RADIAL_BINS


def test_shape_mismatch_raises() -> None:
    image = np.ones((64, 64))
    mask = np.ones((32, 32), dtype=bool)
    with pytest.raises(ValueError, match="shape"):
        reduce(image, mask)


def test_peak_positions_within_tolerance() -> None:
    """After reduction, peaks should appear near the expected ring q-values."""
    image, _ = generate_data(shape=(256, 256))
    calibrated, mask = calibrate(image)
    q, intensity = reduce(calibrated, mask, n_bins=128)

    for q_expected in RING_Q_VALUES:
        # Find the nearest q bin to the expected peak
        nearest_bin = int(np.argmin(np.abs(q - q_expected)))
        # The local maximum near this bin should be within tolerance
        half_window = max(1, int(PEAK_TOLERANCE_Q / (q[1] - q[0])))
        lo = max(0, nearest_bin - half_window)
        hi = min(len(intensity), nearest_bin + half_window + 1)
        local_peak_q = q[lo:hi][np.argmax(intensity[lo:hi])]
        assert abs(local_peak_q - q_expected) <= PEAK_TOLERANCE_Q, (
            f"Peak near q={q_expected:.2f} not found within tolerance "
            f"(nearest peak at q={local_peak_q:.3f})"
        )


def test_dead_pixel_excluded_from_reduction() -> None:
    """An extreme value at a dead pixel must not shift any peak position."""
    from pipeline.constants import DEAD_PIXELS

    image, _ = generate_data(shape=(256, 256))
    calibrated, mask = calibrate(image)

    # Baseline reduction
    q_ref, I_ref = reduce(calibrated, mask, n_bins=128)

    # Inject an extreme value at a known dead pixel
    poisoned = calibrated.copy()
    dead_row, dead_col = DEAD_PIXELS[0]
    poisoned[dead_row, dead_col] = 1e9  # would dominate that bin if included

    # The mask already marks this pixel False — reduction should be unchanged
    q_test, I_test = reduce(poisoned, mask, n_bins=128)
    np.testing.assert_array_equal(q_ref, q_test)
    np.testing.assert_allclose(I_ref, I_test, rtol=1e-6)


def test_uniform_image_uniform_output() -> None:
    """A perfectly flat image should produce a nearly flat I(q)."""
    image = np.ones((128, 128)) * 100.0
    mask = np.ones((128, 128), dtype=bool)
    _, intensity = reduce(image, mask)
    # Allow some edge effects at very small q
    np.testing.assert_allclose(intensity[5:], 100.0, rtol=0.05)
