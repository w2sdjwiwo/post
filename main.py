import os
import instaloader
import pytesseract
import firebase_admin
from firebase_admin import credentials, firestore
from PIL import Image
import json

# 1. Setup Firebase using the GitHub Secret
if not firebase_admin._apps:
    service_account_info = json.loads(os.environ['FIREBASE_SERVICE_ACCOUNT'])
    cred = credentials.Certificate(service_account_info)
    firebase_admin.initialize_app(cred)

db = firestore.client()

# 2. Get Post URL from GitHub Environment
post_url = os.environ.get("POST_URL")
L = instaloader.Instaloader(download_video_thumbnails=False, save_metadata=False)

try:
    # Extract shortcode and download
    shortcode = post_url.split("/")[-2] if post_url.endswith("/") else post_url.split("/")[-1]
    post = instaloader.Post.from_shortcode(L.context, shortcode)
    L.download_post(post, target="temp_posts")

    # 3. Find Image & Run OCR
    image_file = [f for f in os.listdir("temp_posts") if f.endswith(".jpg")][0]
    img_path = os.path.join("temp_posts", image_file)
    
    # Extracting donor name/amount from image text
    raw_text = pytesseract.image_to_string(Image.open(img_path))

    # 4. Upload to Firestore (Jamdudhai Donor Collection)
    db.collection("donors").add({
        "insta_url": post_url,
        "image_url": post.url, # Temporary URL, better to upload to Firebase Storage later
        "content": raw_text,
        "timestamp": firestore.SERVER_TIMESTAMP
    })
    print("✅ Donor data synced to Jamdudhai Firestore!")

except Exception as e:
    print(f"❌ Error: {e}")
