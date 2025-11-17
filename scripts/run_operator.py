#!/usr/bin/env python3
"""
Module 2 CLI: Run the chat operator for a configured platform.

Usage:
    uv run python scripts/run_operator.py "Platform Name"
    uv run python scripts/run_operator.py "WhatsApp Web" --manual-wait 90
"""

import argparse
import sys

from src.config.settings import settings
from src.module2_operator.operator import ChatOperator
from src.utils.exceptions import (
    PlatformNotConfiguredException,
    RecalibrationRequiredException,
)
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


def main() -> int:
    """Main entry point for chat operator."""
    parser = argparse.ArgumentParser(
        description="Run the chat operator for a configured platform",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run operator for WhatsApp Web
  uv run python scripts/run_operator.py "WhatsApp Web"

  # Run with longer manual login wait time
  uv run python scripts/run_operator.py "WhatsApp Web" --manual-wait 120

Note:
  - Ensure you have run analyze_platform.py first to generate the config
  - The operator will wait for manual login (e.g., QR code scan) if needed
  - Press Ctrl+C to stop the operator gracefully
        """,
    )

    parser.add_argument("platform_name", help="Name of the chat platform")
    parser.add_argument(
        "--manual-wait",
        type=int,
        default=60,
        help="Seconds to wait for manual login (default: 60)",
    )

    args = parser.parse_args()

    try:
        logger.info("=" * 60)
        logger.info(f"ChatOperator for {args.platform_name}")
        logger.info("=" * 60)

        # Initialize operator
        operator = ChatOperator(
            platform_name=args.platform_name, cache_dir=settings.cache_dir_path
        )

        # Run operator
        logger.info("Starting operator...")
        logger.info("Press Ctrl+C to stop")
        logger.info("-" * 60)

        operator.run(manual_login_wait=args.manual_wait)

        logger.info("=" * 60)
        logger.info("Operator stopped successfully")
        return 0

    except PlatformNotConfiguredException as e:
        logger.error(f"❌ Configuration Error: {e}")
        logger.info("\nTo fix this, run:")
        logger.info(
            f"  uv run python scripts/analyze_platform.py '{args.platform_name}' <URL>"
        )
        return 1

    except RecalibrationRequiredException as e:
        logger.error(f"❌ Recalibration Required: {e}")
        logger.info("\nSelectors have become outdated. To recalibrate, run:")
        logger.info(
            f"  uv run python scripts/analyze_platform.py '{args.platform_name}' <URL>"
        )
        return 2

    except KeyboardInterrupt:
        logger.info("\n⏹️  Operator stopped by user")
        return 0

    except Exception as e:
        logger.error(f"❌ Operator failed: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
