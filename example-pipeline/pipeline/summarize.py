"""Summary statistics for a reduced 1D I(q) curve.

Finds peaks, computes signal-to-noise ratio, and writes a JSON summary file.
"""
from __future__ import annotations

import json
import logging
from pathlib import Path

import numpy as np
from scipy.signal import find_peaks

from pipeline.constants import PEAK_TOLERANCE_Q, RING_Q_VALUES, SNR_FLOOR

log = logging.getLogger(__name__)


def summarize(
    q_arr: np.ndarray,
    I_arr: np.ndarray,
    output_path: Path | None = None,
) -> dict[str, object]:
    """Compute summary statistics from a 1D I(q) curve.

    Detects peaks, checks them against expected ``RING_Q_VALUES``, and
    computes I_max, I_mean, and an estimate of signal-to-noise ratio.
    Optionally writes results as JSON.

    Parameters
    ----------
    q_arr : np.ndarray
        Radial coordinate array, shape (N,).
    I_arr : np.ndarray
        Intensity array, shape (N,).
    output_path : Path or None
        If provided, write the summary dict as JSON to this path.

    Returns
    -------
    dict[str, object]
        Summary with keys:
        - ``I_max`` (float): maximum intensity value
        - ``I_mean`` (float): mean intensity over all bins
        - ``snr`` (float): I_max / background_rms
        - ``peaks_detected`` (list[float]): q-values of detected peaks
        - ``peaks_matched`` (list[float]): q-values matched to expected ring positions
        - ``n_peaks_expected`` (int): number of expected ring peaks

    Raises
    ------
    ValueError
        If ``q_arr`` and ``I_arr`` have different lengths.
    """
    if len(q_arr) != len(I_arr):
        raise ValueError(
            f"q_arr length {len(q_arr)} != I_arr length {len(I_arr)}"
        )

    log.info("Summarizing I(q) curve with %d bins", len(q_arr))

    I_max = float(I_arr.max())
    I_mean = float(I_arr.mean())

    # SNR: I_max / I_mean, using only non-zero bins to avoid empty outer-ring bins
    nonzero = I_arr[I_arr > 0]
    I_mean_nonzero = float(nonzero.mean()) if len(nonzero) > 0 else 1.0
    snr = I_max / I_mean_nonzero if I_mean_nonzero > 0 else 0.0

    # Peak detection (prominence-based)
    peak_indices, _ = find_peaks(I_arr, prominence=I_arr.std())
    peaks_q = [float(q_arr[i]) for i in peak_indices]

    # Match detected peaks to expected ring positions
    matched: list[float] = []
    for q_detected in peaks_q:
        if any(
            abs(q_detected - q_expected) <= PEAK_TOLERANCE_Q
            for q_expected in RING_Q_VALUES
        ):
            matched.append(q_detected)

    log.info(
        "Summary: I_max=%.2f I_mean=%.2f SNR=%.2f peaks=%d matched=%d/%d",
        I_max,
        I_mean,
        snr,
        len(peaks_q),
        len(matched),
        len(RING_Q_VALUES),
    )

    if snr < SNR_FLOOR:
        log.warning("SNR %.2f is below floor %.2f", snr, SNR_FLOOR)

    summary: dict[str, object] = {
        "I_max": I_max,
        "I_mean": I_mean,
        "snr": snr,
        "peaks_detected": peaks_q,
        "peaks_matched": matched,
        "n_peaks_expected": len(RING_Q_VALUES),
    }

    if output_path is not None:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(summary, indent=2))
        log.info("Summary written to %s", output_path)

    return summary
