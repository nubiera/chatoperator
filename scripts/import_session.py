#!/usr/bin/env python3
"""
Import browser cookies from a JSON file into ChatOperator session storage.

Usage:
    # Export cookies from your browser first (use Cookie-Editor extension)
    # Then run:
    uv run python scripts/import_session.py "Tinder" cookies.json

    # Or import from Chrome profile directly:
    uv run python scripts/import_session.py "Tinder" --chrome-profile
"""

import argparse
import json
import sys
from pathlib import Path

from src.utils.session_manager import SessionManager
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


def import_from_json(platform_name: str, cookie_file: Path) -> bool:
    """Import cookies from a JSON file.

    Args:
        platform_name: Platform name (e.g., "Tinder")
        cookie_file: Path to JSON file with cookies

    Returns:
        True if successful
    """
    try:
        # Read cookies from file
        with open(cookie_file, 'r') as f:
            cookies = json.load(f)

        # Handle different JSON formats
        # Cookie-Editor exports as array of cookie objects
        if isinstance(cookies, dict) and 'cookies' in cookies:
            cookies = cookies['cookies']

        if not isinstance(cookies, list):
            logger.error("Invalid cookie format. Expected list of cookie objects.")
            return False

        logger.info(f"Found {len(cookies)} cookies in {cookie_file}")

        # Save to session manager
        session_manager = SessionManager()
        session_file = session_manager.get_session_file(platform_name)

        import pickle
        with open(session_file, 'wb') as f:
            pickle.dump(cookies, f)

        logger.info(f"✓ Successfully imported session for {platform_name}")
        logger.info(f"  Session file: {session_file}")
        logger.info(f"  Cookies: {len(cookies)}")

        return True

    except Exception as e:
        logger.error(f"Failed to import cookies: {e}")
        return False


def extract_from_chrome_profile(platform_name: str, profile_path: str | None = None) -> bool:
    """Extract cookies from Chrome profile database.

    Args:
        platform_name: Platform name
        profile_path: Path to Chrome profile (auto-detect if None)

    Returns:
        True if successful
    """
    try:
        import sqlite3
        import shutil
        from pathlib import Path

        # Auto-detect Chrome profile if not provided
        if not profile_path:
            import platform as plat
            system = plat.system()

            if system == "Darwin":  # macOS
                profile_path = Path.home() / "Library/Application Support/Google/Chrome/Default"
            elif system == "Windows":
                profile_path = Path.home() / "AppData/Local/Google/Chrome/User Data/Default"
            else:  # Linux
                profile_path = Path.home() / ".config/google-chrome/Default"

        profile_path = Path(profile_path)
        cookies_db = profile_path / "Cookies"

        if not cookies_db.exists():
            # Try "Network/Cookies" for newer Chrome versions
            cookies_db = profile_path / "Network/Cookies"

        if not cookies_db.exists():
            logger.error(f"Chrome cookies database not found at {profile_path}")
            logger.info("Try specifying the profile path manually:")
            logger.info("  --chrome-profile /path/to/Chrome/Profile")
            return False

        # Copy database to avoid lock issues
        temp_db = Path("/tmp/cookies_temp.db")
        shutil.copy2(cookies_db, temp_db)

        # Extract cookies
        conn = sqlite3.connect(str(temp_db))
        cursor = conn.cursor()

        # Query cookies for the domain
        domain = _get_domain_for_platform(platform_name)

        cursor.execute(
            """
            SELECT name, value, host_key, path, expires_utc,
                   is_secure, is_httponly, samesite
            FROM cookies
            WHERE host_key LIKE ?
            """,
            (f"%{domain}%",)
        )

        rows = cursor.fetchall()
        conn.close()
        temp_db.unlink()

        if not rows:
            logger.warning(f"No cookies found for domain: {domain}")
            logger.info("Make sure you're logged in to the site in Chrome")
            return False

        # Convert to Selenium cookie format
        cookies = []
        for row in rows:
            cookie = {
                'name': row[0],
                'value': row[1],
                'domain': row[2],
                'path': row[3],
                'expiry': row[4],
                'secure': bool(row[5]),
                'httpOnly': bool(row[6]),
            }
            cookies.append(cookie)

        logger.info(f"Extracted {len(cookies)} cookies from Chrome profile")

        # Save to session manager
        session_manager = SessionManager()
        session_file = session_manager.get_session_file(platform_name)

        import pickle
        with open(session_file, 'wb') as f:
            pickle.dump(cookies, f)

        logger.info(f"✓ Successfully imported session from Chrome for {platform_name}")
        logger.info(f"  Session file: {session_file}")

        return True

    except Exception as e:
        logger.error(f"Failed to extract from Chrome profile: {e}")
        return False


def _get_domain_for_platform(platform_name: str) -> str:
    """Get domain name for a platform.

    Args:
        platform_name: Platform name

    Returns:
        Domain string
    """
    # Map common platform names to domains
    domain_map = {
        'tinder': 'tinder.com',
        'whatsapp': 'web.whatsapp.com',
        'telegram': 'web.telegram.org',
        'discord': 'discord.com',
        'facebook': 'facebook.com',
        'instagram': 'instagram.com',
    }

    return domain_map.get(platform_name.lower(), platform_name.lower())


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Import browser cookies into ChatOperator session storage",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )

    parser.add_argument(
        "platform_name",
        help="Platform name (e.g., 'Tinder', 'WhatsApp Web')"
    )

    parser.add_argument(
        "cookie_file",
        nargs="?",
        help="Path to JSON file with exported cookies"
    )

    parser.add_argument(
        "--chrome-profile",
        nargs="?",
        const=True,
        help="Extract cookies from Chrome profile (auto-detect path or specify)"
    )

    args = parser.parse_args()

    try:
        if args.chrome_profile:
            # Extract from Chrome profile
            profile_path = args.chrome_profile if isinstance(args.chrome_profile, str) else None
            success = extract_from_chrome_profile(args.platform_name, profile_path)
        elif args.cookie_file:
            # Import from JSON file
            cookie_file = Path(args.cookie_file)
            if not cookie_file.exists():
                logger.error(f"Cookie file not found: {cookie_file}")
                sys.exit(1)
            success = import_from_json(args.platform_name, cookie_file)
        else:
            logger.error("Please provide either a cookie file or --chrome-profile")
            parser.print_help()
            sys.exit(1)

        if success:
            logger.info("\n" + "=" * 60)
            logger.info("NEXT STEPS")
            logger.info("=" * 60)
            logger.info("Run the archiver (no login needed!):")
            logger.info(f"  uv run python scripts/archive_conversations.py '{args.platform_name}'")
            logger.info("=" * 60)

        sys.exit(0 if success else 1)

    except KeyboardInterrupt:
        logger.info("\nImport cancelled")
        sys.exit(0)
    except Exception as e:
        logger.error(f"Import failed: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
