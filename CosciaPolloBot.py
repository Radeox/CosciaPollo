import os
import sys
import re
import requests
import telepot
from time import sleep
from random import randint
from settings import token, hot_words, image_url


def handle(msg):
    content_type, chat_type, chat_id = telepot.glance(msg)

    chat_id = msg['chat']['id']
    command_input = msg['text']

    # Check if a Hot word is in the message
    if re.findall(hot_words, command_input.lower()):
        bot.sendPhoto(chat_id, get_random_image())


# Get random image
def get_random_image():
    r = requests.get(image_url, stream=True)
    r = r.content

    # Get all <img>
    pattern = '<img .+?>'
    found = re.findall(pattern, str(r))

    # Get all 'src' from <img>
    pattern = 'src=\"(.+?)\"'
    found = re.findall(pattern, str(r))

    return found[randint(0, len(found)-1)]


# Main
print("Starting CosciaPolloBot...")

# PID file
pid = str(os.getpid())
pidfile = "/tmp/cosciapollobot.pid"

# Check if PID exist
if os.path.isfile(pidfile):
    print("%s already exists, exiting!" % pidfile)
    sys.exit()

# Create PID file
f = open(pidfile, 'w')
f.write(pid)

# Start working
try:
    bot = telepot.Bot(token)
    bot.message_loop(handle)

    while 1:
        sleep(10)
finally:
    os.unlink(pidfile)
