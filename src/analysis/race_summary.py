"""Analyze Formula 1 lap data and extract race summary statistics."""

from __future__ import annotations

import logging
from typing import Any

import pandas as pd

logger = logging.getLogger(__name__)

# Required columns for analysis
REQUIRED_COLUMNS = {"Driver", "Team", "LapNumber", "Compound", "PitInTime", "PitOutTime"}


def _validate_dataframe(df: pd.DataFrame) -> None:
    """Validate that the DataFrame contains required columns.

    Args:
        df: The lap data DataFrame.

    Raises:
        ValueError: If required columns are missing.
    """
    missing_columns = REQUIRED_COLUMNS - set(df.columns)
    if missing_columns:
        raise ValueError(f"DataFrame is missing required columns: {missing_columns}")


def get_total_drivers(df: pd.DataFrame) -> int:
    """Get the total number of unique drivers in the race.

    Args:
        df: FastF1 lap data DataFrame.

    Returns:
        The number of unique drivers.

    Raises:
        ValueError: If 'Driver' column is missing.
    """
    _validate_dataframe(df)
    total = df["Driver"].nunique()
    logger.info("Total unique drivers: %d", total)
    return total


def get_total_teams(df: pd.DataFrame) -> int:
    """Get the total number of unique teams in the race.

    Args:
        df: FastF1 lap data DataFrame.

    Returns:
        The number of unique teams.

    Raises:
        ValueError: If 'Team' column is missing.
    """
    _validate_dataframe(df)
    total = df["Team"].nunique()
    logger.info("Total unique teams: %d", total)
    return total


def get_total_laps(df: pd.DataFrame) -> int:
    """Get the total number of laps in the race data.

    Args:
        df: FastF1 lap data DataFrame.

    Returns:
        The maximum lap number (assuming laps are numbered sequentially from 1).

    Raises:
        ValueError: If 'LapNumber' column is missing.
    """
    _validate_dataframe(df)
    total = int(df["LapNumber"].max())
    logger.info("Total laps in race: %d", total)
    return total


def get_tire_compounds(df: pd.DataFrame) -> list[str]:
    """Get the list of tire compounds used in the race.

    Args:
        df: FastF1 lap data DataFrame.

    Returns:
        A sorted list of unique tire compound names (e.g., ['SOFT', 'MEDIUM', 'HARD']).

    Raises:
        ValueError: If 'Compound' column is missing.
    """
    _validate_dataframe(df)
    compounds = sorted(df["Compound"].dropna().unique().tolist())
    logger.info("Tire compounds used: %s", compounds)
    return compounds


def get_total_pit_stops(df: pd.DataFrame) -> int:
    """Get the total number of pit stops during the race.

    A pit stop is detected when both PitInTime and PitOutTime are not null.

    Args:
        df: FastF1 lap data DataFrame.

    Returns:
        The total count of pit stops.

    Raises:
        ValueError: If 'PitInTime' or 'PitOutTime' columns are missing.
    """
    _validate_dataframe(df)
    pit_stops = df[(df["PitInTime"].notna()) & (df["PitOutTime"].notna())].shape[0]
    logger.info("Total pit stops: %d", pit_stops)
    return pit_stops


def get_race_summary(df: pd.DataFrame) -> dict[str, Any]:
    """Generate a comprehensive race summary combining all statistics.

    Args:
        df: FastF1 lap data DataFrame.

    Returns:
        A dictionary containing race statistics:
            - total_drivers: Number of unique drivers
            - total_teams: Number of unique teams
            - total_laps: Total number of laps
            - tire_compounds: List of tire compounds used
            - total_pit_stops: Total pit stops in the race

    Raises:
        ValueError: If required columns are missing.
    """
    _validate_dataframe(df)

    logger.info("Generating race summary...")

    summary = {
        "total_drivers": get_total_drivers(df),
        "total_teams": get_total_teams(df),
        "total_laps": get_total_laps(df),
        "tire_compounds": get_tire_compounds(df),
        "total_pit_stops": get_total_pit_stops(df),
    }

    logger.info("Race summary generated: %s", summary)
    return summary
