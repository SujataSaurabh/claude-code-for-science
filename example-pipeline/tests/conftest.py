"""Shared pytest fixtures for the pipeline test suite."""
from __future__ import annotations

import numpy as np
import pytest

from pipeline.calibrate import calibrate
from pipeline.constants import IMAGE_SIZE, RNG_SEED
from pipeline.generate_data import generate_data


@pytest.fixture(scope="session")
def raw_image() -> np.ndarray:
    """Synthetic detector image generated with the canonical seed."""
    image, _ = generate_data(shape=IMAGE_SIZE, seed=RNG_SEED)
    return image


@pytest.fixture(scope="session")
def calibrated_pair(raw_image: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Calibrated image and dead-pixel mask."""
    return calibrate(raw_image)


@pytest.fixture(scope="session")
def small_image() -> np.ndarray:
    """Small 64×64 image for fast unit tests."""
    image, _ = generate_data(shape=(64, 64), seed=RNG_SEED)
    return image


@pytest.fixture(scope="session")
def small_mask() -> np.ndarray:
    """All-valid mask for 64×64 images (no dead pixels at this scale)."""
    return np.ones((64, 64), dtype=bool)
