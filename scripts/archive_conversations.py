#!/usr/bin/env python3
"""Archive conversations from a chat platform.

Downloads all conversations with profile pictures, bios, and full message history.
Exports to markdown format organized by user.

Usage:
    uv run python scripts/archive_conversations.py "Platform Name" [OPTIONS]

Examples:
    # Archive all conversations
    uv run python scripts/archive_conversations.py "Tinder"

    # Archive with manual login (QR code scan)
    uv run python scripts/archive_conversations.py "Tinder" --manual-wait 120

    # Archive limited number of conversations
    uv run python scripts/archive_conversations.py "Tinder" --max-conversations 10

    # Archive to custom directory
    uv run python scripts/archive_conversations.py "Tinder" --output ./my_archives
"""

import argparse
import logging
import sys
from pathlib import Path

from src.config.settings import settings
from src.module2_operator.cache_loader import load_platform_config
from src.module3_archiver.archiver import ConversationArchiver
from src.selenium_utils.driver_factory import (
    create_driver,
    save_driver_session,
    has_saved_session,
)
from src.utils.exceptions import PlatformNotConfiguredException, ArchiverException
from src.utils.logger import setup_logger

logger = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Archive conversations from a chat platform",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    parser.add_argument(
        "platform_name",
        help="Name of the platform to archive (must have cached config)"
    )

    parser.add_argument(
        "--output",
        "-o",
        default="./conversations",
        help="Output directory for archived conversations (default: ./conversations)"
    )

    parser.add_argument(
        "--max-conversations",
        "-m",
        type=int,
        help="Maximum number of conversations to archive (default: all)"
    )

    parser.add_argument(
        "--manual-wait",
        type=int,
        default=60,
        help="Seconds to wait for manual login (QR code, etc.) (default: 60)"
    )

    parser.add_argument(
        "--no-headless",
        action="store_true",
        help="Run browser in visible mode (useful for debugging)"
    )

    parser.add_argument(
        "--fresh-login",
        action="store_true",
        help="Force fresh login (ignore saved session)"
    )

    return parser.parse_args()


def main():
    """Main entry point for conversation archiver."""
    args = parse_args()

    # Setup logging
    setup_logger(settings.log_level)

    logger.info("=" * 60)
    logger.info("ChatOperator - Conversation Archiver")
    logger.info("=" * 60)

    driver = None

    try:
        # Load platform configuration
        logger.info(f"Loading configuration for: {args.platform_name}")
        config = load_platform_config(args.platform_name)

        # Verify archive selectors exist
        if not config.archive_selectors:
            logger.error(
                f"\n❌ Platform '{args.platform_name}' not configured for archiving.\n"
                f"\nRun the analyzer with archive support:\n"
                f"  uv run python scripts/analyze_platform.py \"{args.platform_name}\" "
                f"\"{config.url}\" --archive\n"
            )
            sys.exit(1)

        # Check for saved session
        has_session = has_saved_session(args.platform_name)
        load_session = has_session and not args.fresh_login

        if load_session:
            logger.info(f"✓ Found saved session for {args.platform_name}")
        elif args.fresh_login:
            logger.info("Using --fresh-login, ignoring saved session")
        else:
            logger.info(f"No saved session for {args.platform_name}")

        # Create WebDriver with session support
        logger.info("Starting web browser...")
        headless = not args.no_headless
        driver = create_driver(
            headless=headless,
            platform_name=args.platform_name,
            url=str(config.url),
            load_session=load_session,
        )

        # Wait for manual authentication if no session loaded
        if not load_session:
            logger.info(f"\n{'=' * 60}")
            logger.info("MANUAL LOGIN REQUIRED")
            logger.info(f"{'=' * 60}")
            logger.info(f"Please log in to {args.platform_name} in the browser window.")
            logger.info(f"You have {args.manual_wait} seconds...")
            logger.info(f"{'=' * 60}\n")

            import time
            time.sleep(args.manual_wait)

            # Save session after manual login
            logger.info("Saving session for future use...")
            save_driver_session(driver, args.platform_name)
        else:
            logger.info("✓ Session loaded, skipping manual login")
            import time
            time.sleep(3)  # Brief wait to ensure page is fully loaded

        # Initialize archiver
        output_dir = Path(args.output)
        logger.info(f"Initializing archiver (output: {output_dir})")

        archiver = ConversationArchiver(driver, config, output_dir)

        # Archive conversations
        logger.info("\nStarting conversation archive process...")

        archived_count = archiver.archive_all_conversations(
            max_conversations=args.max_conversations
        )

        # Summary
        logger.info(f"\n{'=' * 60}")
        logger.info("ARCHIVE COMPLETE")
        logger.info(f"{'=' * 60}")
        logger.info(f"✓ Successfully archived {archived_count} conversations")
        logger.info(f"✓ Saved to: {output_dir}")
        logger.info(f"{'=' * 60}\n")

    except PlatformNotConfiguredException as e:
        logger.error(f"\n❌ {e}\n")
        sys.exit(1)

    except ArchiverException as e:
        logger.error(f"\n❌ Archive failed: {e}\n")
        sys.exit(1)

    except KeyboardInterrupt:
        logger.info("\n\n⚠️  Archive interrupted by user")
        sys.exit(0)

    except Exception as e:
        logger.error(f"\n❌ Unexpected error: {e}", exc_info=True)
        sys.exit(1)

    finally:
        if driver:
            # Save session before closing (in case state changed)
            try:
                save_driver_session(driver, args.platform_name)
            except Exception as e:
                logger.debug(f"Could not save session: {e}")

            logger.info("Closing browser...")
            driver.quit()


if __name__ == "__main__":
    main()
