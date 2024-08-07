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
    for trigger in TRIGGERS:
        for hotword in trigger["HOT_WORDS"]:
            if hotword in update.message.text.lower():
                link = get_random_image(trigger["SOURCE_LINK"])
                if link:
                    await update.message.reply_photo(photo=link)


def get_random_image(url):
    """
    Get random image from image result page
    """
    img = None
    header = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 4.4; Nexus 5 Build/_BuildID)"
        + " AppleWebKit/537.36 (KHTML, like Gecko)"
        + " Version/4.0 Chrome/30.0.0.0 Mobile Safari/537.36"
    }

    # Request site
    response = requests.get(url, headers=header)

    # Get all <img>
    pattern = "<img .*>"
    found = re.findall(pattern, str(response.content))

    # Get all 'src' from <img>
    pattern = 'src="(.+?)"'
    found = re.findall(pattern, str(found))

    # Filter those without 'http'
    found = [f for f in found if "http" in f]

    while found:
        img = found.pop(randint(0, len(found) - 1))
        if is_url_image(img):
            break

    if img is None:
        return None
    else:
        return img


def is_url_image(image_url):
    image_formats = ("image/png", "image/jpeg", "image/jpg")

    try:
        r = requests.head(image_url)
    except Exception as e:
        logger.error(e)
        return False

    if r.headers["content-type"] in image_formats:
        return True

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
