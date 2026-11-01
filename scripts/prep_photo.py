
import sys
import cv2
import numpy as np
from PIL import Image
from rembg import remove
from io import BytesIO

def prepare_photo(input_path):
    print("Loading photo...")

    # Open original image
    with open(input_path, "rb") as file:
        original = file.read()

    # Remove background
    print("Removing background...")
    output = remove(original)

    # Convert to PIL image
    image = Image.open(BytesIO(output)).convert("RGBA")

    # Resize image
    image.thumbnail((500, 700))

    # Create white background
    background = Image.new("RGBA", image.size, (255, 255, 255, 255))
    background.alpha_composite(image)

    # Convert to grayscale
    gray = cv2.cvtColor(
        np.array(background.convert("RGB")),
        cv2.COLOR_RGB2GRAY
    )

    # Improve contrast using CLAHE
    clahe = cv2.createCLAHE(
        clipLimit=2.0,
        tileGridSize=(8, 8)
    )
    enhanced = clahe.apply(gray)

    # Save prepared image
    cv2.imwrite("source-prepped.png", enhanced)

    print("Success! source-prepped.png created.")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python scripts/prep_photo.py source-photo.jpg")
    else:
        prepare_photo(sys.argv[1])
