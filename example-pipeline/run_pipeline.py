"""Run the full synthetic beamline pipeline end-to-end.

Stages: generate → calibrate → reduce → summarize.
All data is synthetic; no real detector data is used.

Usage
-----
    python run_pipeline.py
    python run_pipeline.py --output-dir /tmp/results
"""
from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

from pipeline.calibrate import calibrate
from pipeline.generate_data import generate_data
from pipeline.reduce import reduce
from pipeline.summarize import summarize

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(name)s %(levelname)s %(message)s",
)
log = logging.getLogger(__name__)


def run(output_dir: Path) -> dict[str, object]:
    """Execute the full pipeline and return the summary dict.

    Parameters
    ----------
    output_dir : Path
        Directory for output files (created if it does not exist).

    Returns
    -------
    dict[str, object]
        Summary statistics from the final stage.
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    log.info("=== Stage 1: generate synthetic detector image ===")
    image, metadata = generate_data()

    log.info("=== Stage 2: calibrate (flat-field + dead-pixel mask) ===")
    calibrated, mask = calibrate(image)

    log.info("=== Stage 3: azimuthal integration ===")
    q_arr, I_arr = reduce(calibrated, mask)

    log.info("=== Stage 4: summarize ===")
    summary = summarize(q_arr, I_arr, output_path=output_dir / "summary.json")

    log.info(
        "Pipeline complete. Peaks matched: %d / %d",
        len(summary["peaks_matched"]),
        summary["n_peaks_expected"],
    )
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Synthetic beamline pipeline")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("output"),
        help="Directory for output files (default: ./output)",
    )
    args = parser.parse_args()

    try:
        summary = run(args.output_dir)
        print(f"Done. Summary written to {args.output_dir / 'summary.json'}")
        n_matched = len(summary["peaks_matched"])
        n_expected = summary["n_peaks_expected"]
        print(f"  Peaks matched: {n_matched} / {n_expected}")
        print(f"  SNR: {summary['snr']:.2f}")
    except Exception:
        log.exception("Pipeline failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
