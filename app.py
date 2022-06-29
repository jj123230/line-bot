from datetime import datetime

from flask import Flask, abort, request

line_channel_secret = 'cc1d8b57614278cab126252aa4610364'
line_token = 'H4IKf9kD11BsYCvNFaKoHvxb4LCnbt90RhTqpbvamFpdOHkpplrK/pN+yJ/hKtZujU8tVAA64VZ2ZHP2nZgtHELCDrRK'+\
    'BdjsNMrBmOvaqKmAldGuLl/YgsCAaJFKJNs/2aU/nMM6c9kNyhjm+6XIMAdB04t89/1O/w1cDnyilFU='

# https://github.com/line/line-bot-sdk-python
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

app = Flask(__name__)

line_bot_api = LineBotApi(line_token)
handler = WebhookHandler(line_channel_secret)


@app.route("/", methods=["GET", "POST"])
def callback():

    if request.method == "GET":
        return "Hello Heroku"
    if request.method == "POST":
        signature = request.headers["X-Line-Signature"]
        body = request.get_data(as_text=True)

        try:
            handler.handle(body, signature)
        except InvalidSignatureError:
            abort(400)

        return "OK"


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    get_message = event.message.text

    # Send To Line
    reply = TextSendMessage(text=f"{get_message}")
    line_bot_api.reply_message(event.reply_token, reply)
