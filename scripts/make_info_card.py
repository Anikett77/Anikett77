
import os
import html

OUTPUT_FILE = "info-card.svg"

WIDTH = 490
HEIGHT = 390

STATIC = os.getenv("STATIC", "0") == "1"

# Your profile information
PROFILE = {
    "name": "Aniket Chaturvedi",
    "role": "Full-Stack Developer | AI/ML Enthusiast",
    "education": "B.Tech | OIST Bhopal",
    "stack": "Python, C++, React, Next.js, Node.js",
    "database": "MongoDB, MySQL",
    "projects": "Uplyft AI, Navix AI, AutoXplore",
    "interests": "Generative AI, ML, Web Development",
    "status": "Building | Learning | Shipping"
}

# Colors
BG = "#0d1117"
BORDER = "#30363d"
GREEN = "#3fb950"
CYAN = "#58a6ff"
WHITE = "#e6edf3"
GRAY = "#8b949e"
YELLOW = "#d29922"


def text_element(x, y, content, color, size=13, weight="normal"):
    content = html.escape(content)

    return f"""
    <text x="{x}" y="{y}"
          fill="{color}"
          font-family="Courier New, monospace"
          font-size="{size}"
          font-weight="{weight}">
        {content}
    </text>
    """


def create_card():

    print("Creating Neofetch information card...")

    svg = []

    svg.append(f"""
    <svg xmlns="http://www.w3.org/2000/svg"
         width="{WIDTH}"
         height="{HEIGHT}"
         viewBox="0 0 {WIDTH} {HEIGHT}">

        <rect width="100%" height="100%"
              rx="12"
              fill="{BG}"
              stroke="{BORDER}"
              stroke-width="2"/>

        <style>
            text {{
                font-family: 'Courier New', monospace;
            }}

            .row {{
                animation: appear 0.6s ease-out both;
            }}

            @keyframes appear {{
                from {{
                    opacity: 0.15;
                    transform: translateY(7px);
                }}
                to {{
                    opacity: 1;
                    transform: translateY(0);
                }}
            }}
        </style>
    """)

    # Terminal header
    svg.append(f"""
        <circle cx="22" cy="22" r="6" fill="#ff5f56"/>
        <circle cx="42" cy="22" r="6" fill="#ffbd2e"/>
        <circle cx="62" cy="22" r="6" fill="#27c93f"/>

        <text x="245" y="27"
              fill="{GRAY}"
              font-size="12"
              text-anchor="middle">
            anikett77@github — bash
        </text>

        <line x1="0" y1="45" x2="{WIDTH}" y2="45"
              stroke="{BORDER}"/>
    """)

    # Profile heading
    svg.append(text_element(
        25, 83, "anikett77@github", GREEN, 19, "bold"
    ))

    svg.append(text_element(
        25, 108, "~ $ whoami", GRAY, 13
    ))

    svg.append(text_element(
        25, 145, PROFILE["name"], CYAN, 20, "bold"
    ))

    svg.append(text_element(
        25, 169, PROFILE["role"], WHITE, 12
    ))

    # Information rows
    rows = [
        ("EDUCATION", PROFILE["education"]),
        ("STACK", PROFILE["stack"]),
        ("DATABASE", PROFILE["database"]),
        ("PROJECTS", PROFILE["projects"]),
        ("INTERESTS", PROFILE["interests"]),
        ("STATUS", PROFILE["status"])
    ]

    start_y = 215
    spacing = 27

    for index, (label, value) in enumerate(rows):

        y = start_y + index * spacing

        group = f"""
        <g class="row">
            {text_element(25, y, label, GREEN, 12, "bold")}
            {text_element(125, y, value, WHITE, 11)}
        """

        if not STATIC:
            group += f"""
            <animate attributeName="opacity"
                     from="0.15"
                     to="1"
                     begin="{index * 0.18:.2f}s"
                     dur="0.5s"
                     fill="freeze"/>
            """

        group += "</g>"

        svg.append(group)

    # Bottom terminal prompt
    svg.append(text_element(
        25, 378, "anikett77@github ~ $ _", YELLOW, 12
    ))

    svg.append("</svg>")

    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        file.write("\n".join(svg))

    print(f"Success! {OUTPUT_FILE} generated.")


if __name__ == "__main__":
    create_card()
