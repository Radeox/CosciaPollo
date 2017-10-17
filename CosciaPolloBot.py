import os
import sys
import re
import json

from time import sleep
from random import randint

import urllib3
from bs4 import BeautifulSoup

import telepot
from settings import TOKEN, HOT_WORDS, IMAGE_URL


def handle(msg):
    """
    Handle messages from users
    """
    content_type, chat_type, chat_id = telepot.glance(msg)
    command_input = msg['text']

    # Check if a Hot word is in the message
    if re.findall(HOT_WORDS, command_input.lower()):
        bot.sendPhoto(chat_id, get_random_image(IMAGE_URL))


def get_random_image(url):
    """
    Get random image from Google image result page
    """
    header = {'User-Agent':"Mozilla/5.0 (Windows NT 6.1; WOW64)\
               AppleWebKit/537.36 (KHTML, like Gecko)\
               Chrome/43.0.2357.134\
               Safari/537.36"
             }

    soup = get_soup(url, header)
    found = []

    for a in soup.find_all("div", {"class":"rg_meta"}):
        link = json.loads(a.text)["ou"]
        found.append(link)

    return found[randint(0, len(found)-1)]


def get_soup(url, header=None):
    """
    Get soup from url
    """
    http = urllib3.PoolManager()
    response = http.request('GET', url, headers=header)

    return BeautifulSoup(response.data, 'lxml')


# Main
print("Starting CosciaPolloBot...")

# PID file
PID = str(os.getpid())
PIDFILE = "/tmp/cosciapollobot.pid"

# Check if PID exist
if os.path.isfile(PIDFILE):
    print("%s already exists, exiting!" % PIDFILE)
    sys.exit()

# Create PID file
with open(PIDFILE, 'w') as f:
    f.write(PID)
    f.close()

# Start working
try:
    bot = telepot.Bot(TOKEN)
    bot.message_loop(handle)

    while 1:
        sleep(10)
finally:
    os.unlink(PIDFILE)
