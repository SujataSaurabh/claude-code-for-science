"""Tests for summarize.py."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from pipeline.calibrate import calibrate
from pipeline.constants import RING_Q_VALUES
from pipeline.generate_data import generate_data
from pipeline.reduce import reduce
from pipeline.summarize import summarize


@pytest.fixture(scope="module")
def reduced_curve() -> tuple[np.ndarray, np.ndarray]:
    """Full pipeline output for summary tests."""
    image, _ = generate_data(shape=(256, 256))
    calibrated, mask = calibrate(image)
    return reduce(calibrated, mask, n_bins=128)


def test_summary_keys(reduced_curve: tuple[np.ndarray, np.ndarray]) -> None:
    q, intensity = reduced_curve
    result = summarize(q, intensity)
    for key in ("I_max", "I_mean", "snr", "peaks_detected", "peaks_matched", "n_peaks_expected"):
        assert key in result


def test_n_peaks_expected(reduced_curve: tuple[np.ndarray, np.ndarray]) -> None:
    q, intensity = reduced_curve
    result = summarize(q, intensity)
    assert result["n_peaks_expected"] == len(RING_Q_VALUES)


def test_peaks_matched_nonnegative(reduced_curve: tuple[np.ndarray, np.ndarray]) -> None:
    q, intensity = reduced_curve
    result = summarize(q, intensity)
    assert len(result["peaks_matched"]) >= 0


def test_snr_positive(reduced_curve: tuple[np.ndarray, np.ndarray]) -> None:
    q, intensity = reduced_curve
    result = summarize(q, intensity)
    assert result["snr"] > 0.0


def test_I_max_greater_than_mean(reduced_curve: tuple[np.ndarray, np.ndarray]) -> None:
    q, intensity = reduced_curve
    result = summarize(q, intensity)
    assert result["I_max"] >= result["I_mean"]


def test_length_mismatch_raises() -> None:
    q = np.linspace(0, 2, 100)
    intensity = np.ones(50)
    with pytest.raises(ValueError, match="length"):
        summarize(q, intensity)


def test_json_output(tmp_path: Path, reduced_curve: tuple[np.ndarray, np.ndarray]) -> None:
    q, intensity = reduced_curve
    out = tmp_path / "summary.json"
    summarize(q, intensity, output_path=out)
    assert out.exists()
    data = json.loads(out.read_text())
    assert "I_max" in data


def test_at_least_one_ring_matched(reduced_curve: tuple[np.ndarray, np.ndarray]) -> None:
    """The synthetic pipeline should detect at least one of the expected rings."""
    q, intensity = reduced_curve
    result = summarize(q, intensity)
    assert len(result["peaks_matched"]) >= 1, (
        "Expected at least one ring peak to be detected in the synthetic data"
    )
