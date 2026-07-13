"""Analyze pit stop strategies and performance."""

from __future__ import annotations

import logging
from typing import Any

import pandas as pd

logger = logging.getLogger(__name__)


def get_pit_stop_count_by_driver(df: pd.DataFrame) -> dict[str, int]:
    """Get the number of pit stops for each driver.

    Args:
        df: FastF1 lap data DataFrame.

    Returns:
        A dictionary mapping driver names to their pit stop counts.

    Raises:
        ValueError: If required columns are missing.
    """
    if "Driver" not in df.columns or "PitInTime" not in df.columns or "PitOutTime" not in df.columns:
        raise ValueError("DataFrame is missing required pit stop columns")

    pit_stops = {}
    for driver in df["Driver"].unique():
        driver_data = df[df["Driver"] == driver]
        stops = len(driver_data[(driver_data["PitInTime"].notna()) & (driver_data["PitOutTime"].notna())])
        pit_stops[driver] = stops

    logger.info("Calculated pit stop counts for %d drivers", len(pit_stops))
    return pit_stops


def get_pit_stop_duration(df: pd.DataFrame, driver: str | None = None) -> dict[str, Any]:
    """Calculate pit stop durations (PitOutTime - PitInTime).

    Args:
        df: FastF1 lap data DataFrame.
        driver: Optional driver name to filter results.

    Returns:
        A dictionary with pit stop duration statistics.

    Raises:
        ValueError: If required columns are missing or driver not found.
    """
    if "Driver" not in df.columns or "PitInTime" not in df.columns or "PitOutTime" not in df.columns:
        raise ValueError("DataFrame is missing required pit stop columns")

    if driver:
        driver_data = df[df["Driver"] == driver]
        if driver_data.empty:
            raise ValueError(f"Driver '{driver}' not found in race data")
    else:
        driver_data = df

    pit_data = driver_data[(driver_data["PitInTime"].notna()) & (driver_data["PitOutTime"].notna())].copy()

    if pit_data.empty:
        logger.info("No pit stops found for analysis")
        return {"pit_stops": 0, "avg_duration": 0, "min_duration": 0, "max_duration": 0}

    # Calculate duration in seconds
    pit_data["duration"] = (pit_data["PitOutTime"] - pit_data["PitInTime"]).dt.total_seconds()

    stats = {
        "pit_stops": len(pit_data),
        "avg_duration": round(pit_data["duration"].mean(), 2),
        "min_duration": round(pit_data["duration"].min(), 2),
        "max_duration": round(pit_data["duration"].max(), 2),
    }

    if driver:
        logger.info("Calculated pit stop durations for driver '%s': %s", driver, stats)
    else:
        logger.info("Calculated pit stop durations for race: %s", stats)

    return stats


def get_pit_lap_analysis(df: pd.DataFrame) -> list[dict[str, Any]]:
    """Analyze pit stops at specific laps.

    Args:
        df: FastF1 lap data DataFrame.

    Returns:
        A list of pit stop events with lap and driver information.

    Raises:
        ValueError: If required columns are missing.
    """
    if (
        "Driver" not in df.columns
        or "LapNumber" not in df.columns
        or "PitInTime" not in df.columns
        or "PitOutTime" not in df.columns
    ):
        raise ValueError("DataFrame is missing required columns")

    pit_events = []
    pit_data = df[(df["PitInTime"].notna()) & (df["PitOutTime"].notna())].copy()

    for _, row in pit_data.iterrows():
        pit_events.append(
            {
                "driver": row["Driver"],
                "lap": int(row["LapNumber"]),
                "pit_in_time": row["PitInTime"],
                "pit_out_time": row["PitOutTime"],
            }
        )

    pit_events.sort(key=lambda x: x["lap"])
    logger.info("Found %d pit stop events", len(pit_events))
    return pit_events


def get_pit_stop_strategy_summary(df: pd.DataFrame) -> dict[str, Any]:
    """Generate a comprehensive pit stop strategy summary.

    Args:
        df: FastF1 lap data DataFrame.

    Returns:
        A dictionary with pit stop strategy statistics.

    Raises:
        ValueError: If required columns are missing.
    """
    if "Driver" not in df.columns or "PitInTime" not in df.columns or "PitOutTime" not in df.columns:
        raise ValueError("DataFrame is missing required pit stop columns")

    pit_stops_by_driver = get_pit_stop_count_by_driver(df)
    total_stops = sum(pit_stops_by_driver.values())

    summary = {
        "total_pit_stops": total_stops,
        "drivers_with_stops": sum(1 for count in pit_stops_by_driver.values() if count > 0),
        "avg_stops_per_driver": round(total_stops / len(pit_stops_by_driver), 2) if pit_stops_by_driver else 0,
        "max_stops": max(pit_stops_by_driver.values()) if pit_stops_by_driver else 0,
        "min_stops": min(pit_stops_by_driver.values()) if pit_stops_by_driver else 0,
    }

    logger.info("Generated pit stop strategy summary: %s", summary)
    return summary
