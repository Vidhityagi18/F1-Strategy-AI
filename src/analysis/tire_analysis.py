"""Analyze tire strategies and performance across the race."""

from __future__ import annotations

import logging
from typing import Any

import pandas as pd

logger = logging.getLogger(__name__)


def get_tire_usage_by_driver(df: pd.DataFrame) -> dict[str, dict[str, int]]:
    """Get tire compound usage for each driver.

    Args:
        df: FastF1 lap data DataFrame.

    Returns:
        A dictionary mapping driver names to their tire compound usage counts.

    Raises:
        ValueError: If required columns are missing.
    """
    if "Driver" not in df.columns or "Compound" not in df.columns:
        raise ValueError("DataFrame is missing 'Driver' or 'Compound' column")

    usage = {}
    for driver in df["Driver"].unique():
        driver_data = df[df["Driver"] == driver]
        usage[driver] = driver_data["Compound"].value_counts().to_dict()

    logger.info("Calculated tire usage for %d drivers", len(usage))
    return usage


def get_tire_compound_statistics(df: pd.DataFrame) -> dict[str, Any]:
    """Get aggregate statistics for each tire compound used.

    Args:
        df: FastF1 lap data DataFrame.

    Returns:
        A dictionary with statistics for each tire compound:
            - drivers_used: Number of drivers using the compound
            - total_laps: Total laps on that compound
            - avg_laps_per_driver: Average laps per driver

    Raises:
        ValueError: If required columns are missing.
    """
    if "Compound" not in df.columns or "Driver" not in df.columns:
        raise ValueError("DataFrame is missing 'Compound' or 'Driver' column")

    compounds = df["Compound"].dropna().unique()
    stats = {}

    for compound in compounds:
        compound_data = df[df["Compound"] == compound]
        unique_drivers = compound_data["Driver"].nunique()
        total_laps = len(compound_data)
        avg_laps = total_laps / unique_drivers if unique_drivers > 0 else 0

        stats[compound] = {
            "drivers_used": unique_drivers,
            "total_laps": total_laps,
            "avg_laps_per_driver": round(avg_laps, 2),
        }

    logger.info("Calculated statistics for %d tire compounds", len(stats))
    return stats


def get_most_common_tire_strategy(df: pd.DataFrame) -> dict[str, int]:
    """Get the most common tire strategy (compound progression) in the race.

    Args:
        df: FastF1 lap data DataFrame.

    Returns:
        A dictionary mapping compounds to the number of drivers using that progression.

    Raises:
        ValueError: If required columns are missing.
    """
    if "Driver" not in df.columns or "Compound" not in df.columns:
        raise ValueError("DataFrame is missing 'Driver' or 'Compound' column")

    strategies = {}
    for driver in df["Driver"].unique():
        driver_data = df[df["Driver"] == driver].sort_values("LapNumber")
        strategy = tuple(driver_data["Compound"].dropna().unique())
        strategy_str = " → ".join(strategy)
        strategies[strategy_str] = strategies.get(strategy_str, 0) + 1

    logger.info("Found %d unique tire strategies", len(strategies))
    return strategies


def get_tire_change_events(df: pd.DataFrame) -> list[dict[str, Any]]:
    """Get all tire change events (where a driver switched compounds).

    Args:
        df: FastF1 lap data DataFrame.

    Returns:
        A list of dictionaries containing tire change events.

    Raises:
        ValueError: If required columns are missing.
    """
    if "Driver" not in df.columns or "Compound" not in df.columns or "LapNumber" not in df.columns:
        raise ValueError("DataFrame is missing required columns")

    changes = []
    for driver in df["Driver"].unique():
        driver_data = df[df["Driver"] == driver].sort_values("LapNumber")
        compounds = driver_data["Compound"].values
        lap_numbers = driver_data["LapNumber"].values

        for i in range(1, len(compounds)):
            if pd.notna(compounds[i]) and pd.notna(compounds[i - 1]) and compounds[i] != compounds[i - 1]:
                changes.append(
                    {
                        "driver": driver,
                        "lap": int(lap_numbers[i]),
                        "from_compound": compounds[i - 1],
                        "to_compound": compounds[i],
                    }
                )

    logger.info("Found %d tire change events", len(changes))
    return changes
