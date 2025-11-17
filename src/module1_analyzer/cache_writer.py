"""Configuration cache writer."""

import json
from pathlib import Path

from src.models.platform_config import PlatformConfig
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


def write_cache(config: PlatformConfig, cache_dir: Path) -> Path:
    """
    Write PlatformConfig to JSON cache file.

    Args:
        config: Platform configuration to write
        cache_dir: Directory to write cache file

    Returns:
        Path to written cache file
    """
    # Ensure cache directory exists
    cache_dir.mkdir(parents=True, exist_ok=True)

    # Generate filename from platform name
    filename = config.platform_name.lower().replace(" ", "_").replace("-", "_")
    cache_file = cache_dir / f"{filename}.json"

    logger.info(f"Writing cache to {cache_file}")

    # Convert to dict with proper JSON encoding
    config_dict = config.model_dump(mode="json")

    # Write formatted JSON
    with open(cache_file, "w", encoding="utf-8") as f:
        json.dump(config_dict, f, indent=2, ensure_ascii=False)

    logger.info(f"Cache successfully written ({cache_file.stat().st_size} bytes)")
    return cache_file


def read_cache(cache_file: Path) -> PlatformConfig:
    """
    Read PlatformConfig from JSON cache file.

    Args:
        cache_file: Path to cache file

    Returns:
        Platform configuration

    Raises:
        FileNotFoundError: If cache file doesn't exist
        ValueError: If cache file is invalid
    """
    if not cache_file.exists():
        raise FileNotFoundError(f"Cache file not found: {cache_file}")

    logger.info(f"Reading cache from {cache_file}")

    with open(cache_file, encoding="utf-8") as f:
        config_dict = json.load(f)

    # Validate and create PlatformConfig
    config = PlatformConfig(**config_dict)

    logger.info(f"Cache successfully loaded: {config.platform_name}")
    return config


def validate_cache(cache_file: Path) -> bool:
    """
    Validate cache file without loading.

    Args:
        cache_file: Path to cache file

    Returns:
        True if valid, False otherwise
    """
    try:
        read_cache(cache_file)
        return True
    except Exception as e:
        logger.error(f"Cache validation failed: {e}")
        return False
