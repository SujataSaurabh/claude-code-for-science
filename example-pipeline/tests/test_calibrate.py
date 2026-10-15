"""Tests for calibrate.py."""
from __future__ import annotations

import numpy as np
import pytest

from pipeline.calibrate import calibrate, make_mask
from pipeline.constants import CALIBRATION_SCALE, DEAD_PIXELS, IMAGE_SIZE


def test_make_mask_shape() -> None:
    mask = make_mask(IMAGE_SIZE)
    assert mask.shape == IMAGE_SIZE
    assert mask.dtype == bool


def test_make_mask_dead_pixels_false() -> None:
    mask = make_mask(IMAGE_SIZE)
    for row, col in DEAD_PIXELS:
        assert not mask[row, col], f"Expected dead pixel ({row},{col}) to be False"


def test_make_mask_valid_pixels_true() -> None:
    mask = make_mask(IMAGE_SIZE)
    dead_set = set(DEAD_PIXELS)
    valid_count = sum(
        1
        for r in range(IMAGE_SIZE[0])
        for c in range(IMAGE_SIZE[1])
        if (r, c) not in dead_set and mask[r, c]
    )
    expected_valid = IMAGE_SIZE[0] * IMAGE_SIZE[1] - len(DEAD_PIXELS)
    assert valid_count == expected_valid


def test_calibrate_scale() -> None:
    """Every pixel should be multiplied by CALIBRATION_SCALE."""
    image = np.ones(IMAGE_SIZE)
    calibrated, _ = calibrate(image)
    np.testing.assert_allclose(calibrated[~make_mask(IMAGE_SIZE)], CALIBRATION_SCALE, rtol=1e-6)
    # A valid pixel not in the dead list should also be scaled
    np.testing.assert_allclose(calibrated[0, 0], CALIBRATION_SCALE, rtol=1e-6)


def test_calibrate_dead_pixels_not_zeroed() -> None:
    """Dead pixels must NOT be zeroed — only masked."""
    image = np.ones(IMAGE_SIZE) * 100.0
    calibrated, mask = calibrate(image)
    for row, col in DEAD_PIXELS:
        # The data value at a dead pixel is preserved (scaled), not set to zero
        assert calibrated[row, col] > 0.0, (
            f"Dead pixel ({row},{col}) was zeroed; it should be masked, not zeroed"
        )
        assert not mask[row, col]


def test_calibrate_returns_correct_shape() -> None:
    image = np.zeros(IMAGE_SIZE)
    calibrated, mask = calibrate(image)
    assert calibrated.shape == IMAGE_SIZE
    assert mask.shape == IMAGE_SIZE


def test_calibrate_shape_mismatch_raises() -> None:
    image = np.zeros((64, 64))
    bad_mask = np.ones((32, 32), dtype=bool)
    with pytest.raises(ValueError, match="shape"):
        calibrate(image, mask=bad_mask)


def test_calibrate_custom_scale() -> None:
    image = np.ones((32, 32))
    mask = np.ones((32, 32), dtype=bool)
    calibrated, _ = calibrate(image, scale=2.0, mask=mask)
    np.testing.assert_allclose(calibrated, 2.0)
