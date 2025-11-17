#!/usr/bin/env python3
"""
Module 1 CLI: Analyze a chat platform interface and generate config cache.

Usage:
    uv run python scripts/analyze_platform.py "Platform Name" "https://platform.url"
    uv run python scripts/analyze_platform.py "WhatsApp Web" "https://web.whatsapp.com" --wait 10
"""

import argparse
import sys

from src.config.settings import settings
from src.module1_analyzer.analyzer import InterfaceAnalyzer
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


def main() -> int:
    """Main entry point for platform analysis."""
    parser = argparse.ArgumentParser(
        description="Analyze a chat platform interface and generate config cache",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze WhatsApp Web
  uv run python scripts/analyze_platform.py "WhatsApp Web" "https://web.whatsapp.com"

  # Analyze with custom wait time
  uv run python scripts/analyze_platform.py "Telegram Web" "https://web.telegram.org" --wait 10

  # Analyze with visible browser (for debugging)
  uv run python scripts/analyze_platform.py "Discord" "https://discord.com/app" --no-headless
        """,
    )

    parser.add_argument("platform_name", help="Name of the chat platform")
    parser.add_argument("url", help="URL of the chat platform")
    parser.add_argument(
        "--wait",
        type=int,
        default=5,
        help="Seconds to wait after page load for dynamic content (default: 5)",
    )
    parser.add_argument(
        "--no-headless",
        action="store_true",
        help="Run browser in visible mode (useful for debugging)",
    )
    parser.add_argument(
        "--focus",
        default="body",
        help="CSS selector to focus DOM extraction (default: body)",
    )

    args = parser.parse_args()

    try:
        # Check API key
        if not settings.GEMINI_API_KEY:
            logger.error("GEMINI_API_KEY not set in environment")
            logger.error("Please set GEMINI_API_KEY in .env file")
            return 1

        # Initialize analyzer
        analyzer = InterfaceAnalyzer(
            gemini_api_key=settings.GEMINI_API_KEY, cache_dir=settings.cache_dir_path
        )

        # Test Gemini connection
        logger.info("Testing Gemini API connection...")
        if not analyzer.test_gemini_connection():
            logger.error("Gemini API connection test failed")
            return 1

        logger.info("✅ Gemini API connected")

        # Run analysis
        logger.info(f"Analyzing platform: {args.platform_name}")
        logger.info(f"URL: {args.url}")

        config = analyzer.analyze_platform(
            platform_name=args.platform_name,
            url=args.url,
            wait_after_load=args.wait,
            headless=not args.no_headless,
            focus_selector=args.focus,
        )

        # Display results
        print("\n" + "=" * 60)
        print("✅ ANALYSIS COMPLETE!")
        print("=" * 60)
        print(f"Platform: {config.platform_name}")
        print(f"URL: {config.url}")
        print(f"Last Updated: {config.last_updated}")
        print("\nSelectors Found:")
        for name, selector in config.selectors.model_dump().items():
            if selector:
                print(f"  • {name}: {selector[:60]}...")
        print("\nCache Location:")
        print(
            f"  {settings.cache_dir_path / (args.platform_name.lower().replace(' ', '_') + '.json')}"
        )
        print("\nNext Steps:")
        print("  1. Validate the config:")
        print(
            f"     uv run python scripts/validate_config.py "
            f"{settings.cache_dir_path / (args.platform_name.lower().replace(' ', '_') + '.json')}"
        )
        print("  2. Run the operator:")
        print(f"     uv run python scripts/run_operator.py '{args.platform_name}'")
        print("=" * 60)

        return 0

    except KeyboardInterrupt:
        logger.info("\nAnalysis interrupted by user")
        return 130
    except Exception as e:
        logger.error(f"Analysis failed: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
