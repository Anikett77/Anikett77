
import json
import re
from datetime import datetime
from pathlib import Path

import requests
from bs4 import BeautifulSoup

USERNAME = "Anikett77"
URL = f"https://github.com/users/{USERNAME}/contributions"

OUTPUT = Path("data/contributions.json")


def get_level(count):
    if count == 0:
        return 0
    elif count <= 2:
        return 1
    elif count <= 5:
        return 2
    elif count <= 9:
        return 3
    elif count <= 14:
        return 4
    return 5


def main():
    print(f"Fetching contributions for {USERNAME}...")

    response = requests.get(
        URL,
        headers={"User-Agent": "Mozilla/5.0"},
        timeout=30
    )

    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    cells = soup.select(".ContributionCalendar-day")

    if not cells:
        raise RuntimeError("No contribution cells found.")

    contributions = []

    for cell in cells:

        day = cell.get("data-date")
        cell_id = cell.get("id")

        if not day or not cell_id:
            continue

        # Find the tooltip connected to this contribution cell.
        tooltip = soup.find(
            "tool-tip",
            attrs={"for": cell_id}
        )

        if not tooltip:
            raise RuntimeError(
                f"Tooltip not found for {day}"
            )

        tooltip_text = tooltip.get_text(" ", strip=True)

        # Extract the actual contribution count.
        match = re.search(
            r"([\d,]+)\s+contributions?",
            tooltip_text,
            re.IGNORECASE
        )

        if match:
            count = int(match.group(1).replace(",", ""))
        elif "no contributions" in tooltip_text.lower():
            count = 0
        else:
            raise RuntimeError(
                f"Could not parse tooltip for {day}: {tooltip_text}"
            )

        contributions.append({
            "date": day,
            "count": count,
            "level": get_level(count)
        })

    if not contributions:
        raise RuntimeError("No contribution data extracted.")

    # Remove duplicate dates and sort chronologically.
    unique = {
        item["date"]: item
        for item in contributions
    }

    contributions = sorted(
        unique.values(),
        key=lambda item: item["date"]
    )

    total = sum(
        item["count"]
        for item in contributions
    )

    OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    data = {
        "username": USERNAME,
        "total": total,
        "updated_at": datetime.now().isoformat(),
        "contributions": contributions
    }

    OUTPUT.write_text(
        json.dumps(data, indent=4),
        encoding="utf-8"
    )

    print("\nContribution data fetched successfully!")
    print(f"Days collected: {len(contributions)}")
    print(f"Total contributions: {total}")
    print(f"Saved to: {OUTPUT}")


if __name__ == "__main__":
    main()
