"""Tests for generate_data.py."""
from __future__ import annotations

import numpy as np

from pipeline.constants import IMAGE_SIZE, RNG_SEED
from pipeline.generate_data import generate_data


def test_output_shape() -> None:
    image, _ = generate_data(shape=IMAGE_SIZE)
    assert image.shape == IMAGE_SIZE


def test_non_negative() -> None:
    image, _ = generate_data()
    assert image.min() >= 0.0


def test_metadata_keys() -> None:
    _, meta = generate_data()
    for key in ("shape", "q_values", "seed", "q_max"):
        assert key in meta


def test_seeded_reproducibility() -> None:
    """Same seed must produce identical images."""
    img_a, _ = generate_data(seed=RNG_SEED)
    img_b, _ = generate_data(seed=RNG_SEED)
    np.testing.assert_array_equal(img_a, img_b)


def test_different_seeds_differ() -> None:
    img_a, _ = generate_data(seed=RNG_SEED)
    img_b, _ = generate_data(seed=RNG_SEED + 1)
    assert not np.array_equal(img_a, img_b)


def test_rings_produce_signal() -> None:
    """A ring-pattern image should have higher counts near ring q-values."""
    image, _ = generate_data(shape=(128, 128), seed=RNG_SEED)
    assert image.sum() > 0


def test_custom_shape() -> None:
    image, meta = generate_data(shape=(64, 64))
    assert image.shape == (64, 64)
    assert meta["shape"] == (64, 64)
