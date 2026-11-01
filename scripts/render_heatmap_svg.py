
import json
import html
import math
from datetime import datetime, timedelta
import os

# ---------------- CONFIGURATION ----------------

INPUT_FILE = "data/contributions.json"
OUTPUT_FILE = "contrib-heatmap.svg"

PALETTE = [
    "#161b22",
    "#0e4429",
    "#006d32",
    "#26a641",
    "#39d353",
    "#69f0a0"
]

CELL_SIZE = 11
GAP = 3
STEP = CELL_SIZE + GAP

WIDTH = 860
LEFT = 48
TOP = 43

# -----------------------------------------------


def load_data():

    print("Loading contribution data...")

    with open(INPUT_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def generate_svg(data):

    print("Generating contribution heatmap...")

    days = data["contributions"]

    if not days:
        raise ValueError("No contribution data available.")

    # Convert JSON dates into date objects
    contributions = {}

    for day in days:

        date = datetime.strptime(
            day["date"], "%Y-%m-%d"
        ).date()

        contributions[date] = day

    all_dates = sorted(contributions.keys())

    first_date = all_dates[0]
    last_date = all_dates[-1]

    # GitHub calendar starts on Sunday
    sunday_offset = (first_date.weekday() + 1) % 7

    calendar_start = first_date - timedelta(
        days=sunday_offset
    )

    total_calendar_days = (
        last_date - calendar_start
    ).days + 1

    weeks = math.ceil(total_calendar_days / 7)

    if weeks > 53:
        raise ValueError(
            f"Unexpected calendar size: {weeks} weeks"
        )

    # SVG dimensions
    grid_width = weeks * STEP

    height = 175

    svg = []

    svg.append(f"""
    <svg xmlns="http://www.w3.org/2000/svg"
         width="{WIDTH}"
         height="{height}"
         viewBox="0 0 {WIDTH} {height}">

        <rect width="100%" height="100%"
              rx="12"
              fill="#0d1117"
              stroke="#30363d"
              stroke-width="1"/>

        <style>
            text {{
                font-family: Arial, sans-serif;
            }}

            .month {{
                fill: #8b949e;
                font-size: 11px;
            }}

            .day-label {{
                fill: #8b949e;
                font-size: 10px;
            }}

            .cell {{
                animation: reveal 0.4s ease-out both;
            }}

            @keyframes reveal {{
                from {{
                    opacity: 0.15;
                    transform: translateY(-4px);
                }}
                to {{
                    opacity: 1;
                    transform: translateY(0);
                }}
            }}
        </style>
    """)

    # Header
    total = data["total"]

    svg.append(f"""
        <text x="20" y="24"
              fill="#e6edf3"
              font-size="14"
              font-weight="bold">
            {total:,} contributions in the last year
        </text>
    """)

    svg.append(f"""
        <text x="{WIDTH - 20}" y="24"
              fill="#8b949e"
              font-size="10"
              text-anchor="end">
            @{html.escape(data['username'])}
        </text>
    """)

    # Month labels
    for date in all_dates:

        if date.day == 1:

            column = (
                (date - calendar_start).days // 7
            )

            x = LEFT + column * STEP

            svg.append(f"""
                <text x="{x}" y="39"
                      class="month">
                    {date.strftime('%b')}
                </text>
            """)

    # Weekday labels
    weekday_names = {
        1: "Mon",
        3: "Wed",
        5: "Fri"
    }

    for weekday, label in weekday_names.items():

        y = TOP + weekday * STEP + 9

        svg.append(f"""
            <text x="12" y="{y}"
                  class="day-label">
                {label}
            </text>
        """)

    # Contribution cells
    for date in all_dates:

        day = contributions[date]

        day_index = (
            date - calendar_start
        ).days

        column = day_index // 7

        row = (date.weekday() + 1) % 7

        x = LEFT + column * STEP
        y = TOP + row * STEP

        level = max(
            0,
            min(5, int(day["level"]))
        )

        color = PALETTE[level]

        delay = (column * 7 + row) * 0.008

        count = day["count"]

        tooltip = (
            f"{count} contributions on {date.isoformat()}"
        )

        svg.append(f"""
            <g class="cell">

                <rect
                    x="{x}"
                    y="{y}"
                    width="{CELL_SIZE}"
                    height="{CELL_SIZE}"
                    rx="3"
                    fill="{color}"
                    stroke="#30363d"
                    stroke-width="0.35">

                    <title>{html.escape(tooltip)}</title>

                    <animate
                        attributeName="opacity"
                        from="0.15"
                        to="1"
                        begin="{delay:.3f}s"
                        dur="0.4s"
                        fill="freeze"/>

                </rect>

            </g>
        """)

    # Footer statistics
    footer_y = 153

    current_streak = data.get("current_streak", 0)
    longest_streak = data.get("longest_streak", 0)

    svg.append(f"""
        <text x="20" y="{footer_y}"
              fill="#8b949e"
              font-size="10">
            Current streak: {current_streak} days
        </text>

        <text x="175" y="{footer_y}"
              fill="#8b949e"
              font-size="10">
            Longest streak: {longest_streak} days
        </text>
    """)

    # Legend
    legend_x = WIDTH - 185

    svg.append(f"""
        <text x="{legend_x - 30}" y="{footer_y}"
              fill="#8b949e"
              font-size="10">
            Less
        </text>
    """)

    for level, color in enumerate(PALETTE):

        x = legend_x + level * 15

        svg.append(f"""
            <rect x="{x}" y="{footer_y - 10}"
                  width="11" height="11"
                  rx="3"
                  fill="{color}"/>
        """)

    svg.append(f"""
        <text x="{legend_x + 100}" y="{footer_y}"
              fill="#8b949e"
              font-size="10">
            More
        </text>
    """)

    svg.append("</svg>")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        file.write("\n".join(svg))

    print("--------------------------------")
    print("Heatmap successfully generated!")
    print("--------------------------------")
    print(f"Calendar weeks: {weeks}")
    print(f"Total contributions: {total:,}")
    print(f"Output: {OUTPUT_FILE}")


if __name__ == "__main__":

    if not os.path.exists(INPUT_FILE):

        print("Contribution JSON not found!")
        print("Run fetch_contributions.py first.")

    else:

        try:
            data = load_data()
            generate_svg(data)

        except Exception as error:
            print(f"Error: {error}")
            raise
