import logging
import os
import re
from random import randint

import requests
from telegram import Update
from telegram.ext import Application, MessageHandler, filters

from triggers import TRIGGERS

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

logger = logging.getLogger(__name__)


async def msgHandler(update: Update, _):
    """
    Check if a Hot word is in the message
    """
    if not update.message or not update.message.text:
        return

    text = update.message.text.lower()
    logger.info(f"Received message from {update.effective_user.first_name}: {text}")

    for trigger in TRIGGERS:
        for hotword in trigger["HOT_WORDS"]:
            if hotword in text:
                logger.info(f"Trigger matched: {hotword}")
                link = get_random_image(trigger["SOURCE_LINK"])
                if link:
                    logger.info(f"Sending image: {link}")
                    await update.message.reply_photo(photo=link)
                else:
                    logger.warning(f"No image found for trigger: {hotword}")
                return # Stop after first match


def get_random_image(url):
    """
    Get random image from image result page
    """
    img = None
    header = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    # Request site
    try:
        response = requests.get(url, headers=header, timeout=10)
        response.raise_for_status()
    except Exception as e:
        logger.error(f"Error fetching URL: {e}")
        return None

    # Get all 'src' from <img> tags using a more robust regex
    found = re.findall(r'src="([^"]+)"', response.text)
    # Also look for data-src which Google often uses
    found += re.findall(r'data-src="([^"]+)"', response.text)
    # Bing uses murl (Media URL) in its results
    found += re.findall(r'murl&quot;:&quot;(https?://[^&]+?)&quot;', response.text)

    # Filter those without 'http'
    found = [f for f in found if f.startswith("http")]

    logger.info(f"Found {len(found)} potential image links")

    while found:
        img = found.pop(randint(0, len(found) - 1))
        if is_url_image(img):
            return img

    if img is None:
        return None
    else:
        return img


def is_url_image(image_url):
    image_formats = ("image/png", "image/jpeg", "image/jpg", "image/webp")
    min_size = 20000  # 20 KB
    excluded_keywords = ("favicon", "icon", "logo", "thumbnail")

    if any(keyword in image_url.lower() for keyword in excluded_keywords):
        logger.info(f"Skipping image due to keyword: {image_url}")
        return False

    try:
        r = requests.head(image_url, timeout=5)
        content_type = r.headers.get("content-type", "")
        content_length = int(r.headers.get("content-length", 0))

        if content_type in image_formats:
            if content_length > 0 and content_length < min_size:
                logger.info(f"Skipping small image ({content_length} bytes): {image_url}")
                return False
            return True
        
        logger.debug(f"URL {image_url} is not an image: {content_type}")
    except Exception as e:
        logger.error(f"Error checking image URL: {e}")
        return False

    return False


def main() -> None:
    print("Starting CosciaPolloBot...")
    TOKEN = os.environ["TOKEN"]

    # Setup bot
    application = Application.builder().token(TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT, msgHandler))

    # Start the Bot
    application.run_polling()


if __name__ == "__main__":
    main()
