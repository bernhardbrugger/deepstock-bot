"""CLI entry point for deepstock-bot."""

from __future__ import annotations

import argparse
import sys

from deepstock import __version__
from deepstock.config import load_settings, print_config_status
from deepstock.scanner import DeepStockScanner


def main() -> None:
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="deepstock",
        description="🤖📊 AI-powered stock & crypto intelligence bot",
    )
    parser.add_argument(
        "-v", "--version",
        action="version",
        version=f"deepstock-bot {__version__}",
    )
    parser.add_argument(
        "--env",
        default=None,
        help="Path to .env file (default: .env in current directory)",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    scan_parser = subparsers.add_parser("scan", help="Run a single scan")
    scan_parser.add_argument(
        "--min-value", type=int, default=None,
        help="Minimum trade value to report",
    )

    watch_parser = subparsers.add_parser("watch", help="Continuous monitoring")
    watch_parser.add_argument(
        "--interval", type=int, default=None,
        help="Scan interval in minutes",
    )

    subparsers.add_parser("config", help="Validate configuration")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    settings = load_settings(args.env)

    if args.command == "config":
        print_config_status(settings)
        issues = settings.validate()
        has_errors = any(issue.startswith("❌") for issue in issues)
        sys.exit(1 if has_errors else 0)

    issues = settings.validate()
    errors = [i for i in issues if i.startswith("❌")]
    if errors:
        print("\n".join(errors))
        print("\nRun 'deepstock config' to see full configuration status.")
        sys.exit(1)

    scanner = DeepStockScanner(settings)

    if args.command == "scan":
        if args.min_value is not None:
            settings.min_trade_value = args.min_value
        results = scanner.run_scan()
        print(f"\n✅ Scan complete: {results['trades_filtered']} notable trades found, {results['alerts_sent']} alerts sent.")

    elif args.command == "watch":
        if args.interval is not None:
            settings.scan_interval_minutes = args.interval
        scanner.watch()


if __name__ == "__main__":
    main()
