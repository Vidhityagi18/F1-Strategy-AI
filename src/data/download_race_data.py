"""Reusable utilities for downloading and saving Formula 1 session data."""

from __future__ import annotations

import argparse
import logging
import re
from pathlib import Path
from typing import Final

import pandas as pd

logger = logging.getLogger(__name__)

PROJECT_ROOT: Final[Path] = Path(__file__).resolve().parents[2]
DATA_DIR: Final[Path] = PROJECT_ROOT / "data"
RAW_DATA_DIR: Final[Path] = DATA_DIR / "raw"
PROCESSED_DATA_DIR: Final[Path] = DATA_DIR / "processed"
CACHE_DIR: Final[Path] = RAW_DATA_DIR / "cache"


def setup_cache(cache_dir: Path | None = None) -> Path:
    """Enable FastF1 caching and return the cache directory path.

    Args:
        cache_dir: Optional cache directory override.

    Returns:
        The resolved cache directory used for FastF1.
    """
    resolved_cache_dir = (cache_dir or CACHE_DIR).resolve()
    resolved_cache_dir.mkdir(parents=True, exist_ok=True)

    try:
        import fastf1
    except ImportError as exc:
        logger.error("FastF1 is required to download race data: %s", exc)
        raise RuntimeError("FastF1 must be installed to download race data") from exc

    try:
        fastf1.Cache.enable_cache(str(resolved_cache_dir))
    except Exception as exc:  # pragma: no cover - defensive handling
        logger.warning("Could not enable FastF1 cache at %s: %s", resolved_cache_dir, exc)

    logger.info("FastF1 cache enabled at %s", resolved_cache_dir)
    return resolved_cache_dir


def create_output_directories() -> tuple[Path, Path]:
    """Create the raw and processed data directories if they do not exist."""
    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
    logger.info("Ensured data directories exist: %s and %s", RAW_DATA_DIR, PROCESSED_DATA_DIR)
    return RAW_DATA_DIR, PROCESSED_DATA_DIR


def generate_output_filename(season: int, grand_prix: str, session_type: str) -> Path:
    """Generate a sanitized CSV filename for a given session.

    Args:
        season: The Formula 1 season year.
        grand_prix: The grand prix name.
        session_type: The session type such as Race or Qualifying.

    Returns:
        A path under the processed data directory.
    """
    sanitized_gp = re.sub(r"[^a-zA-Z0-9]+", "_", grand_prix).strip("_").lower()
    sanitized_session = re.sub(r"[^a-zA-Z0-9]+", "_", session_type).strip("_").lower()
    filename = f"{season}_{sanitized_gp}_{sanitized_session}.csv"
    return PROCESSED_DATA_DIR / filename


def download_race(season: int, grand_prix: str, session_type: str) -> pd.DataFrame:
    """Download a Formula 1 session, save its lap data, and return the dataframe.

    Args:
        season: The Formula 1 season year.
        grand_prix: The grand prix name, such as "Monaco".
        session_type: The session type such as "Race", "Qualifying", or "Practice".

    Returns:
        A pandas DataFrame containing lap-level data.

    Raises:
        ValueError: If required arguments are empty.
        RuntimeError: If the session cannot be loaded.
    """
    if not season or not grand_prix.strip() or not session_type.strip():
        raise ValueError("season, grand_prix, and session_type must be provided")

    create_output_directories()
    setup_cache()

    try:
        import fastf1
    except ImportError as exc:
        logger.error("FastF1 is required to download race data: %s", exc)
        raise RuntimeError("FastF1 must be installed") from exc

    logger.info(
        "Attempting to load session for season=%s, grand_prix=%s, session_type=%s",
        season,
        grand_prix,
        session_type,
    )

    try:
        session = fastf1.get_session(season, grand_prix, session_type)
        session.load()
    except Exception as exc:  # pragma: no cover - network and API variability
        logger.exception(
            "Failed to load session for season=%s, grand_prix=%s, session_type=%s",
            season,
            grand_prix,
            session_type,
        )
        raise RuntimeError("Unable to load Formula 1 session data") from exc

    laps = session.laps
    if laps is None:
        raise RuntimeError("Session lap data was not available")

    output_path = generate_output_filename(season, grand_prix, session_type)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        laps.to_csv(output_path, index=False)
    except Exception as exc:  # pragma: no cover - filesystem variability
        logger.exception("Failed to save lap data to %s", output_path)
        raise RuntimeError(f"Unable to save lap data to {output_path}") from exc

    logger.info("Saved lap data to %s", output_path)
    return laps


def main() -> None:
    """CLI entry point for downloading a race session."""
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(name)s - %(message)s")

    parser = argparse.ArgumentParser(description="Download F1 session lap data")
    parser.add_argument("--season", type=int, default=2023, help="Formula 1 season year")
    parser.add_argument("--grand-prix", default="Monaco", help="Grand Prix name")
    parser.add_argument("--session-type", default="Race", help="Session type such as Race or Qualifying")
    args = parser.parse_args()

    download_race(args.season, args.grand_prix, args.session_type)


if __name__ == "__main__":
    main()
