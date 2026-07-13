"""Data loading utilities for F1 race analysis."""

from __future__ import annotations

import logging
from pathlib import Path

import pandas as pd

logger = logging.getLogger(__name__)


def load_race_data(file_path: Path | str) -> pd.DataFrame:
    """Load race lap data from a CSV file.

    Args:
        file_path: Path to the CSV file containing lap data.

    Returns:
        A pandas DataFrame containing the race lap data.

    Raises:
        FileNotFoundError: If the file does not exist.
        ValueError: If the file cannot be read as CSV.
    """
    file_path = Path(file_path)

    if not file_path.exists():
        logger.error("Race data file not found: %s", file_path)
        raise FileNotFoundError(f"Race data file not found: {file_path}")

    try:
        df = pd.read_csv(file_path)
        logger.info("Successfully loaded race data from %s with %d rows", file_path, len(df))
        return df
    except Exception as exc:
        logger.exception("Failed to load race data from %s", file_path)
        raise ValueError(f"Unable to read CSV file: {file_path}") from exc
