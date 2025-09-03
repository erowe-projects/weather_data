import datetime as dt
import statistics
from typing import List, Dict, Tuple
from .logging_config import get_logger

logger = get_logger(__name__)


def compute_range_stats(readings: List[Dict]) -> Tuple[float, float, float, int]:
    """
    Compute mean, min, max, count for a list of readings.
    Returns (mean, min, max, count). None if no readings.
    """
    temps = [r["temp_c"] for r in readings if r.get("temp_c") is not None]
    if not temps:
        logger.warning("No valid temperatures found for range stats")
        return (None, None, None, 0)
    return (
        statistics.fmean(temps),
        min(temps),
        max(temps),
        len(temps),
    )


def compute_daily_stats(readings: List[Dict]) -> List[Dict]:
    """
    Group readings by day and compute daily stats.
    """
    grouped = {}
    for r in readings:
        if r.get("temp_c") is None:
            continue
        d = r["time"].date()
        grouped.setdefault(d, []).append(r["temp_c"])

    results = []
    for d, temps in sorted(grouped.items()):
        results.append(
            {
                "date": d,
                "avg_temp_c": statistics.fmean(temps),
                "min_temp_c": min(temps),
                "max_temp_c": max(temps),
                "count": len(temps),
            }
        )
    logger.info("Computed daily stats for %d days", len(results))
    return results


def weekly_high_low(readings: List[Dict]) -> Tuple[float, float]:
    """
    Return weekly high and low temperatures.
    """
    temps = [r["temp_c"] for r in readings if r.get("temp_c") is not None]
    if not temps:
        logger.warning("No temperatures for weekly high/low")
        return (None, None)
    return (max(temps), min(temps))

