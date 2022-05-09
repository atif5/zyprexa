
import telebot
import requests
import wolframalpha
import parse
from urllib.parse import urlparse


PARSE_MODE = "MarkdownV2"
AVAILABLE_COMMANDS = ["/start", "/solve", "/latex"]

STARTER = """
Hi\! I am zyprexa\, a bot built by [Burzum](https://github.com/atif5)
I can solve and inform you about any mathematical expression with my command with the syntax:
`\/solve (regular expression)`

I can render latex as well\:
`\/latex (latex code)`"""

LATEX_SERVICE = "https://latex.codecogs.com/png.latex?\dpi{300}\huge "


TTOKEN = "bottoken"
WALPHAID = "wolframalphatokenid"

client = wolframalpha.Client(WALPHAID)
zyprexa = telebot.TeleBot(TTOKEN)


@zyprexa.message_handler(commands=["test"])
def test(message):
    zyprexa.reply_to(message, "*I'm up\!*", parse_mode=PARSE_MODE)


@zyprexa.message_handler(commands=["start"])
def greet(message):
    zyprexa.send_message(message.chat.id, STARTER, parse_mode=PARSE_MODE)


def headline(regex):
    response = f"""
Hello!
The question you asked, as I perceived, is: 
{regex}
Just a sec...
                """
    return response


def get_infomap(regex):
    res = client.query(regex)
    infomap = dict([(pod.title, list(pod.subpods)) for pod in res.pods])
    return infomap


def get_byte_stream(src):
    return requests.get(src).content


def send_image(chat, src):
    zyprexa.send_photo(chat.id, get_byte_stream(src))


def send_infomap(chat, infomap):
    for title in infomap:
        if title == "Input":
            continue
        zyprexa.send_message(chat.id, f"`{title}`:", parse_mode=PARSE_MODE)
        subpods = infomap[title]
        for subpod in subpods:
            src = subpod["img"].src
            if subpod.title:
                zyprexa.send_message(
                    chat.id, f"_{subpod.title}_:", parse_mode=PARSE_MODE)
            if not subpod.plaintext:
                send_image(chat, src)
            else:
                ref = zyprexa.send_message(chat.id, subpod.plaintext)
                zyprexa.reply_to(ref, f"[image]({src})", parse_mode=PARSE_MODE)
    zyprexa.send_message(chat.id, "||that's all I got\!||",
                         parse_mode=PARSE_MODE)


@zyprexa.message_handler(commands=["solve"])
def solve(message):
    if not (res := parse.parse("/solve {}", message.text)):
        zyprexa.reply_to(
            message, "You need to input something! for more info try the /start command.")
        return
    regex = res[0]
    zyprexa.reply_to(message, headline(regex))
    infomap = get_infomap(regex)
    send_infomap(message.chat, infomap)


@zyprexa.message_handler(commands=["latex"])
def convert(message):
    if not (res := parse.parse("/latex {}", message.text)):
        zyprexa.reply_to(
            message, "You need to input something! for more info try the /start command.")
        return
    regex = res[0]
    zyprexa.reply_to(message, "Okay! Working on it...")
    global LATEX_SERVICE
    src = LATEX_SERVICE+regex
    
    zyprexa.send_message(message.chat.id, "Here it is:")
    while True:
        try:
            send_image(message.chat, src)
            return
        except requests.exceptions.ConnectionError:
            continue


@zyprexa.message_handler(func=lambda message: message not in AVAILABLE_COMMANDS)
def sorry(message):
    zyprexa.reply_to(
        message, "I don't know what that means :( check out my /start command for more info")


if __name__ == "__main__":
    zyprexa.infinity_polling()
