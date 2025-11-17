"""Configuration cache loader for Module 2."""

import json
from pathlib import Path

from src.models.platform_config import PlatformConfig
from src.utils.exceptions import PlatformNotConfiguredException
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


def load_cache(platform_name: str, cache_dir: Path) -> PlatformConfig:
    """
    Load cached platform configuration.

    Args:
        platform_name: Name of the platform
        cache_dir: Cache directory path

    Returns:
        Platform configuration

    Raises:
        PlatformNotConfiguredException: If cache not found or invalid
    """
    # Generate filename
    filename = platform_name.lower().replace(" ", "_").replace("-", "_")
    cache_file = cache_dir / f"{filename}.json"

    if not cache_file.exists():
        logger.error(f"Cache not found: {cache_file}")
        raise PlatformNotConfiguredException(
            f"No cache found for '{platform_name}'. "
            f"Run Module 1 analyzer first: "
            f"uv run python scripts/analyze_platform.py '{platform_name}' <URL>"
        )

    logger.info(f"Loading cache from {cache_file}")

    try:
        with open(cache_file, encoding="utf-8") as f:
            data = json.load(f)

        config = PlatformConfig(**data)
        logger.info(f"Cache loaded successfully: {config.platform_name}")
        return config

    except Exception as e:
        logger.error(f"Failed to load cache: {e}")
        raise PlatformNotConfiguredException(
            f"Invalid cache file for '{platform_name}': {e}"
        ) from e
