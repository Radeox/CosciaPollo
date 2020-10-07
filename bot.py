import os
import re
from random import randint
from time import sleep

import requests
import telepot

from triggers import TRIGGERS


def handle(msg):
    """
    Handle messages from users
    """
    content_type, chat_type, chat_id = telepot.glance(msg)
    command_input = msg['text']

    for c in command_input.split():
        for trigger in TRIGGERS:
            # Check if a Hot word is in the message
            if re.match("|".join(trigger['HOT_WORDS']).lower(), c.lower()):
                try:
                    print(f"> @ {msg['from']['username']} asked for some {trigger['CONTEXT']}")
                except:
                    print(f"> {msg['from']['first_name']} asked for some {trigger['CONTEXT']}")

                bot.sendPhoto(chat_id, get_random_image(trigger['SOURCE_LINK']))


def get_random_image(url):
    """
    Get random image from image result page
    """
    img = None
    header = { 'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36" }

    # Request site
    response = requests.get(url, headers=header)
    c = response.content

    # Get all <img>
    pattern = '<img .+?>'
    found = re.findall(pattern, str(c))

    # Get all 'src' from <img>
    pattern = 'src=\"(.+?)\"'
    found = re.findall(pattern, str(c))

    while not is_url_image(img):
        img = found[randint(0, len(found)-1)]

    return img


def is_url_image(image_url):
    image_formats = ("image/png", "image/jpeg", "image/jpg")

    try:
        r = requests.head(image_url)
    except:
        return False

    if r.headers["content-type"] in image_formats:
        return True

    return False


print("Starting CosciaPolloBot...")

# Start working
bot = telepot.Bot(os.environ['TOKEN'])
bot.message_loop(handle)

while 1:
    sleep(100)
