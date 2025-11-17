#!/usr/bin/env python3
"""
Validate a platform configuration cache file.

Usage:
    uv run python scripts/validate_config.py src/cache/whatsapp_web.json
"""

import argparse
import json
import sys
from pathlib import Path

from src.models.platform_config import PlatformConfig
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


def main() -> int:
    """Main entry point for config validation."""
    parser = argparse.ArgumentParser(
        description="Validate a platform configuration cache file"
    )
    parser.add_argument("config_file", type=Path, help="Path to config JSON file")
    parser.add_argument(
        "--verbose", "-v", action="store_true", help="Show detailed config contents"
    )

    args = parser.parse_args()

    try:
        # Check file exists
        if not args.config_file.exists():
            logger.error(f"❌ Config file not found: {args.config_file}")
            return 1

        # Load and validate
        logger.info(f"Validating config: {args.config_file}")

        with open(args.config_file, encoding="utf-8") as f:
            data = json.load(f)

        # Validate with Pydantic
        config = PlatformConfig(**data)

        # Display results
        print("\n" + "=" * 60)
        print("✅ CONFIG VALID")
        print("=" * 60)
        print(f"Platform: {config.platform_name}")
        print(f"URL: {config.url}")
        print(f"Last Updated: {config.last_updated}")
        print("\nSelectors:")
        for name, selector in config.selectors.model_dump().items():
            if selector:
                status = "✅"
            else:
                status = "⚠️  (null)"
            print(f"  {status} {name:20} {selector or 'N/A'}")

        print("\nTimeouts:")
        print(f"  • Page Load: {config.wait_timeouts.page_load}s")
        print(f"  • Element Visible: {config.wait_timeouts.element_visible}s")
        print(f"  • Message Send: {config.wait_timeouts.message_send}s")

        if args.verbose:
            print("\nFull Config (JSON):")
            print("-" * 60)
            print(json.dumps(config.model_dump(mode="json"), indent=2))

        print("=" * 60)

        # Warnings
        if not config.selectors.message_bubble_bot:
            print("\n⚠️  Warning: message_bubble_bot is null")
            print("   This is OK if the platform doesn't distinguish")
            print("   between user and bot messages visually.")

        return 0

    except json.JSONDecodeError as e:
        logger.error(f"❌ Invalid JSON: {e}")
        return 1

    except Exception as e:
        logger.error(f"❌ Validation failed: {e}")
        logger.error(f"Error type: {type(e).__name__}")

        # Show specific validation errors for Pydantic
        if hasattr(e, "errors"):
            print("\nValidation Errors:")
            for error in e.errors():
                print(f"  • {error['loc']}: {error['msg']}")

        return 1


if __name__ == "__main__":
    sys.exit(main())
