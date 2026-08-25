from __future__ import annotations

import argparse

from playwright.sync_api import sync_playwright

from browser_session import run_flow
from scenarios import SCENARIOS, resolve_scenarios
from settings import (
    BASE_URL,
    CHROMIUM_LAUNCH_ARGS,
    HEADLESS,
    SLOW_MO_MS,
)
from ui import new_page


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run Folium Playwright e2e scenarios"
    )
    parser.add_argument(
        "--scenario",
        action="append",
        dest="scenario_names",
        help="Run only the named scenario. Repeat the flag to run more than one.",
    )
    parser.add_argument(
        "--list",
        action="store_true",
        help="List available scenarios and exit.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    if args.list:
        print("Available scenarios:")
        for scenario in SCENARIOS:
            print(f"- {scenario.name}")
        return

    scenarios = resolve_scenarios(args.scenario_names)

    print(f"Running Folium e2e scenarios against {BASE_URL}")
    print("Selected scenarios: " + ", ".join(scenario.name for scenario in scenarios))
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            headless=HEADLESS,
            slow_mo=SLOW_MO_MS,
            args=CHROMIUM_LAUNCH_ARGS,
        )
        try:
            for scenario in scenarios:
                page = new_page(browser, BASE_URL)
                try:
                    run_flow(
                        page,
                        BASE_URL,
                        scenario.flow,
                        scenario.name,
                        scenario.runner,
                    )
                finally:
                    page.context.close()
        finally:
            browser.close()

    print("All requested scenarios passed")


if __name__ == "__main__":
    main()
