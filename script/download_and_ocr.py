import requests
import re
import json
import pytesseract
from PIL import Image
from io import BytesIO

# 🔹 CHANGE THIS to your Instagram page
INSTAGRAM_URL = "https://www.instagram.com/shreeramgaushala/"

# Output JSON file
OUTPUT_JSON = "donors.json"


def get_latest_image_url():
    """
    Uses Instagram oEmbed to fetch thumbnail image
    """
    oembed_url = "https://api.instagram.com/oembed/?url=" + INSTAGRAM_URL
    response = requests.get(oembed_url)

    if response.status_code != 200:
        print("❌ oEmbed request failed")
        return None

    data = response.json()

    if "thumbnail_url" not in data:
        print("❌ No thumbnail found")
        return None

    return data["thumbnail_url"]



def download_image(url):
    """Download image and return PIL Image"""
    response = requests.get(url)
    return Image.open(BytesIO(response.content))


def run_gujarati_ocr(image):
    """Extract Gujarati text using Tesseract"""
    text = pytesseract.image_to_string(image, lang="guj")
    return text


def parse_donors(text):
    """Find donor names and ₹ amounts from OCR text"""
    donors = []

    lines = text.split("\n")

    for line in lines:
        line = line.strip()

        # Detect amount
        amount_match = re.search(r"(₹|રૂ)?\s?(\d{2,6})", line)

        # Detect Gujarati name keywords
        name_match = re.search(r"(શ્રી|શ્રીમતી|પરિવાર|દાતાશ્રી).*", line)

        if amount_match and name_match:
            donors.append({
                "name": name_match.group(),
                "amount": amount_match.group(2)
            })

    return donors


def save_json(data):
    """Save donors list to donors.json"""
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def main():
    print("🔄 Checking latest Instagram post...")

    image_url = get_latest_image_url()
    if not image_url:
        return

    print("⬇ Downloading image...")
    image = download_image(image_url)

    print("🔍 Running Gujarati OCR...")
    text = run_gujarati_ocr(image)

    print("🧠 Parsing donor data...")
    donors = parse_donors(text)

    print(f"✅ Found {len(donors)} donors")

    save_json(donors)
    print("💾 donors.json updated")


if __name__ == "__main__":
    main()

