
from PIL import Image
import html
import os

# ---------------- CONFIGURATION ----------------

INPUT_IMAGE = "source-prepped.png"
OUTPUT_SVG = "avi-ascii.svg"

# Character density: bright -> dark
RAMP = " .`:-=+*cs#%@"

# Portrait dimensions
COLS = 100
ROWS = 53

# Character dimensions
CHAR_WIDTH = 10
CHAR_HEIGHT = 16

# Animation settings
ANIMATION_DURATION = 3.5
ROW_DELAY = 0.055

# Monochrome text color
TEXT_COLOR = "#303030"
BACKGROUND = "#ffffff"

# -----------------------------------------------


def image_to_ascii(image_path):

    print("Loading prepared image...")

    # Open image and convert to grayscale
    img = Image.open(image_path).convert("L")

    # Resize image to character grid
    img = img.resize((COLS, ROWS), Image.Resampling.LANCZOS)

    pixels = img.load()

    ascii_rows = []

    print("Converting pixels into ASCII characters...")

    for y in range(ROWS):

        row = ""

        for x in range(COLS):

            brightness = pixels[x, y]

            # Bright pixels -> sparse characters
            # Dark pixels -> dense characters
            index = int((255 - brightness) / 255 * (len(RAMP) - 1))

            character = RAMP[index]

            row += character

        ascii_rows.append(row)

    return ascii_rows


def create_animated_svg(ascii_rows):

    print("Creating animated SVG...")

    width = COLS * CHAR_WIDTH
    height = ROWS * CHAR_HEIGHT

    svg = []

    svg.append(
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}">'
    )

    # Background
    svg.append(
        f'<rect width="100%" height="100%" fill="{BACKGROUND}"/>'
    )

    # Monospace font
    svg.append("""
    <style>
        .ascii {
            font-family: 'Courier New', monospace;
            font-size: 13px;
            font-weight: bold;
            fill: """ + TEXT_COLOR + """;
            white-space: pre;
        }
    </style>
    """)

    for i, row in enumerate(ascii_rows):

        y = (i + 1) * CHAR_HEIGHT - 3

        clip_id = f"clip{i}"

        # Each row gets its own clipping rectangle
        svg.append(f"""
        <defs>
            <clipPath id="{clip_id}">
                <rect x="0" y="{i * CHAR_HEIGHT}"
                      width="0" height="{CHAR_HEIGHT}">
                    <animate
                        attributeName="width"
                        from="0"
                        to="{width}"
                        begin="{i * ROW_DELAY:.3f}s"
                        dur="{ANIMATION_DURATION}s"
                        fill="freeze"/>
                </rect>
            </clipPath>
        </defs>
        """)

        # ASCII text inside clipping area
        svg.append(f"""
        <text
            x="0"
            y="{y}"
            class="ascii"
            clip-path="url(#{clip_id})">{html.escape(row)}</text>
        """)

    svg.append("</svg>")

    # Save SVG
    with open(OUTPUT_SVG, "w", encoding="utf-8") as file:
        file.write("\n".join(svg))

    print(f"Success! {OUTPUT_SVG} generated.")


if __name__ == "__main__":

    if not os.path.exists(INPUT_IMAGE):
        print(f"Error: {INPUT_IMAGE} not found!")
        print("Run prep_photo.py first.")
    else:

        ascii_art = image_to_ascii(INPUT_IMAGE)

        create_animated_svg(ascii_art)

        print("Your animated ASCII portrait is ready!")
