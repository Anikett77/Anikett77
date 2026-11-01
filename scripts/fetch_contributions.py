
import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import json
import re
import os

# ---------------- CONFIGURATION ----------------

USERNAME = "Anikett77"

URL = f"https://github.com/users/{USERNAME}/contributions"

OUTPUT_FILE = "data/contributions.json"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; GitHubProfileArt/1.0)"
}

# -----------------------------------------------


def get_contribution_count(day):

    # First try GitHub's data-count attribute
    data_count = day.get("data-count")

    if data_count is not None:
        try:
            return int(data_count)
        except ValueError:
            pass

    # Otherwise read the accessible label
    label = day.get("aria-label", "")

    match = re.search(
        r"([\d,]+)\s+contributions?",
        label,
        re.IGNORECASE
    )

    if match:
        return int(match.group(1).replace(",", ""))

    return 0


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
    else:
        return 5


def calculate_streaks(days):

    current_streak = 0
    longest_streak = 0
    streak = 0

    today = datetime.now().date()

    active_dates = {
        datetime.strptime(day["date"], "%Y-%m-%d").date()
        for day in days
        if day["count"] > 0
    }

    # Longest streak
    for day in days:

        if day["count"] > 0:
            streak += 1
            longest_streak = max(longest_streak, streak)
        else:
            streak = 0

    # Current streak
    check_date = today

    # If today has no contributions, yesterday may
    # still be the latest active streak date.
    if check_date not in active_dates:
        check_date -= timedelta(days=1)

    while check_date in active_dates:
        current_streak += 1
        check_date -= timedelta(days=1)

    return current_streak, longest_streak


def fetch_contributions():

    print(f"Fetching contributions for {USERNAME}...")

    response = requests.get(
        URL,
        headers=HEADERS,
        timeout=30
    )

    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    # GitHub contribution calendar cells
    cells = soup.select(
        "td.ContributionCalendar-day[data-date], "
        "[data-date][data-level]"
    )

    if not cells:
        raise RuntimeError(
            "No contribution cells found. "
            "GitHub may have changed its HTML structure."
        )

    days = []

    for cell in cells:

        date = cell.get("data-date")

        if not date:
            continue

        count = get_contribution_count(cell)

        days.append({
            "date": date,
            "count": count,
            "level": get_level(count)
        })

    # Remove duplicate dates and sort
    unique_days = {
        day["date"]: day
        for day in days
    }

    days = sorted(
        unique_days.values(),
        key=lambda item: item["date"]
    )

    if not days:
        raise RuntimeError("No valid contribution dates found.")

    total = sum(day["count"] for day in days)

    current_streak, longest_streak = calculate_streaks(days)

    best_day = max(
        days,
        key=lambda item: item["count"]
    )

    data = {
        "username": USERNAME,
        "generated_at": datetime.now().isoformat(),
        "total_contributions": total,
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "best_day": best_day,
        "days": days
    }

    # Create data directory if missing
    os.makedirs("data", exist_ok=True)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:

        json.dump(
            data,
            file,
            indent=4
        )

    print("--------------------------------")
    print("Contribution data fetched!")
    print("--------------------------------")
    print(f"Username: {USERNAME}")
    print(f"Total contributions: {total}")
    print(f"Current streak: {current_streak}")
    print(f"Longest streak: {longest_streak}")
    print(f"Best day: {best_day['date']}")
    print(f"Saved to: {OUTPUT_FILE}")


if __name__ == "__main__":

    try:
        fetch_contributions()

    except requests.RequestException as error:
        print(f"Network error: {error}")

    except Exception as error:
        print(f"Error: {error}")
        raise
