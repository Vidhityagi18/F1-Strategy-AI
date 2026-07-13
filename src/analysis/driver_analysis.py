"""Analyze individual driver performance and statistics."""

from __future__ import annotations

import logging
from typing import Any

import pandas as pd

logger = logging.getLogger(__name__)


def get_driver_lap_count(df: pd.DataFrame, driver: str) -> int:
    """Get the number of laps completed by a driver.

    Args:
        df: FastF1 lap data DataFrame.
        driver: Driver name or abbreviation.

    Returns:
        The number of laps completed by the driver.

    Raises:
        ValueError: If the driver is not found in the data.
    """
    if "Driver" not in df.columns:
        raise ValueError("DataFrame is missing 'Driver' column")

    driver_data = df[df["Driver"] == driver]
    if driver_data.empty:
        logger.warning("Driver '%s' not found in race data", driver)
        raise ValueError(f"Driver '{driver}' not found in race data")

    lap_count = len(driver_data)
    logger.info("Driver '%s' completed %d laps", driver, lap_count)
    return lap_count


def get_driver_pit_stops(df: pd.DataFrame, driver: str) -> int:
    """Get the number of pit stops for a specific driver.

    Args:
        df: FastF1 lap data DataFrame.
        driver: Driver name or abbreviation.

    Returns:
        The number of pit stops made by the driver.

    Raises:
        ValueError: If required columns are missing or driver not found.
    """
    if "Driver" not in df.columns:
        raise ValueError("DataFrame is missing 'Driver' column")
    if "PitInTime" not in df.columns or "PitOutTime" not in df.columns:
        raise ValueError("DataFrame is missing pit stop columns")

    driver_data = df[df["Driver"] == driver]
    if driver_data.empty:
        raise ValueError(f"Driver '{driver}' not found in race data")

    pit_stops = len(driver_data[(driver_data["PitInTime"].notna()) & (driver_data["PitOutTime"].notna())])
    logger.info("Driver '%s' made %d pit stops", driver, pit_stops)
    return pit_stops


def get_driver_tire_strategy(df: pd.DataFrame, driver: str) -> dict[str, int]:
    """Get the tire strategy (compound usage) for a driver.

    Args:
        df: FastF1 lap data DataFrame.
        driver: Driver name or abbreviation.

    Returns:
        A dictionary mapping tire compound names to lap counts.

    Raises:
        ValueError: If required columns are missing or driver not found.
    """
    if "Driver" not in df.columns or "Compound" not in df.columns:
        raise ValueError("DataFrame is missing 'Driver' or 'Compound' column")

    driver_data = df[df["Driver"] == driver]
    if driver_data.empty:
        raise ValueError(f"Driver '{driver}' not found in race data")

    strategy = driver_data["Compound"].value_counts().to_dict()
    logger.info("Driver '%s' tire strategy: %s", driver, strategy)
    return strategy


def get_all_drivers_summary(df: pd.DataFrame) -> dict[str, Any]:
    """Generate a summary for all drivers in the race.

    Args:
        df: FastF1 lap data DataFrame.

    Returns:
        A dictionary mapping driver names to their statistics.

    Raises:
        ValueError: If required columns are missing.
    """
    if "Driver" not in df.columns:
        raise ValueError("DataFrame is missing 'Driver' column")

    drivers = df["Driver"].unique()
    summary = {}

    for driver in drivers:
        try:
            summary[driver] = {
                "lap_count": get_driver_lap_count(df, driver),
                "pit_stops": get_driver_pit_stops(df, driver),
                "tire_strategy": get_driver_tire_strategy(df, driver),
            }
        except ValueError as exc:
            logger.warning("Could not generate summary for driver '%s': %s", driver, exc)
            continue

    logger.info("Generated summary for %d drivers", len(summary))
    return summary
