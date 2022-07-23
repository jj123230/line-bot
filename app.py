import datetime
import os

from apscheduler.schedulers.background import BackgroundScheduler
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import (PostbackEvent, MessageEvent, TextMessage, 
                            TextSendMessage, StickerSendMessage, LocationSendMessage, ImageSendMessage, VideoSendMessage, 
                            TemplateSendMessage, FlexSendMessage, 
                            ButtonsTemplate, CarouselTemplate, CarouselColumn, ImageCarouselTemplate, ImageCarouselColumn, 
                            QuickReply, QuickReplyButton, ConfirmTemplate,
                            MessageAction, MessageTemplateAction, URIAction, PostbackTemplateAction,
                            ImagemapSendMessage, BaseSize, URIImagemapAction, MessageImagemapAction, ImagemapArea, Video, ExternalLink,
                            RichMenuSwitchAction, RichMenu, RichMenuSize, RichMenuArea, RichMenuBounds, RichMenuAlias)

app = Flask(__name__)

line_bot_api = LineBotApi('H4IKf9kD11BsYCvNFaKoHvxb4LCnbt90RhTqpbvamFpdOHkpplrK/pN+yJ/hKtZujU8tVAA64VZ2ZHP2nZgtHELCDrRKBdjsNMrBmOvaqKmAldGuLl/YgsCAaJFKJNs/2aU/nMM6c9kNyhjm+6XIMAdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('cc1d8b57614278cab126252aa4610364')

status = 'chat'
list_7810 = ['list_7', 'list_8', 'list_10']
counting = ['7+', '8+', '7-', '8-', '78+', '7+8+', '78-', '7-8-', '10+', '10-']

list_7, list_8, list_10 = [],[],[]

## Clear
def job():
    [globals()[i].clear() for i in list_7810]
    print('clear!')
    
job()
    
clear = BackgroundScheduler(daemon=True)
clear.add_job(job, "cron", hour = 22)
clear.start()

def nosleep():
    print('clear!')
    
no_sleep = BackgroundScheduler(daemon=True)
no_sleep.add_job(nosleep, "interval", minutes = 20)
no_sleep.start()
    
## Counting and return (Using if-else)
# Why I wrote this code in this ugly form: because I use Heroku as webhook, and the CPU ain't good enough to run the code below (line 146- line 175), 
# thus, I have to wrote in the most efficient way to make the chat bot response without lagging. 
def call(msg, user_id):
    global list_7, list_8, list_10
    if len(msg) == 2:
        if '+' in msg:
            if msg == '7+':
                list_7.append(user_id)
                return '7.00: %s人\n8.30: %s人' % (len(set(list_7)), len(set(list_8)))
            elif msg == '8+':
                list_8.append(user_id)
                return '7.00: %s人\n8.30: %s人' % (len(set(list_7)), len(set(list_8)))
        elif '-' in msg:
            if msg== '7-':
                while user_id in list_7: list_7.remove(user_id)
                return '7.00: %s人\n8.30: %s人' % (len(set(list_7)), len(set(list_8)))
            elif msg== '8-':
                while user_id in list_8: list_8.remove(user_id)
                return '7.00: %s人\n8.30: %s人' % (len(set(list_7)), len(set(list_8)))
    elif len(msg) == 3:
        if '+' in msg:
            if msg == '10+':
                list_10.append(user_id)
                return '10.30: %s人' % len(set(list_10))
            elif msg == '78+':
                list_7.append(user_id)
                list_8.append(user_id)
                return '7.00: %s人\n8.30: %s人' % (len(set(list_7)), len(set(list_8)))
        elif '-' in msg:
            if msg == '10-':
                list_10.append(user_id)
                return '10.30: %s人' % len(set(list_10))
            elif msg == '78-':
                while user_id in list_7: list_7.remove(user_id)
                while user_id in list_8: list_8.remove(user_id)
                return '7.00: %s人\n8.30: %s人' % (len(set(list_7)), len(set(list_8)))
    elif len(msg) == 4:
        if msg == '7+8+':
            list_7.append(user_id)
            list_8.append(user_id)
            return '7.00: %s人\n8.30: %s人' % (len(set(list_7)), len(set(list_8)))
        elif msg == '7-8-':
            while user_id in list_7: list_7.remove(user_id)
            while user_id in list_8: list_8.remove(user_id)
            return '7.00: %s人\n8.30: %s人' % (len(set(list_7)), len(set(list_8)))
        
def recall_78(msg):
    if msg == 10:
        return '10.30: %s人' % len(set(list_10))
    else:
        return '7.00: %s人\n8.30: %s人' % (len(set(list_7)), len(set(list_8)))


# 接收 LINE 的資訊
@app.route("/", methods=['GET', 'POST'])
def call_back():
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
def dscbot(event):
    global list_7, list_8, list_10 ## schedule, status
    msg = event.message.text
    user_id = event.source.user_id
    reply_token = event.reply_token
    
    if msg in counting:
        reply_text = call(msg, user_id)
        line_bot_api.reply_message(reply_token, TextSendMessage(text= reply_text))
        
    elif msg == '指令':
        line_bot_api.reply_message(reply_token, TextSendMessage( \
            text= '教練用: 點名，清空\n學生用: 7+, 8+, 7-, 8-, 78+, 7+8+, 78-, 7-8-, 10+, 10-'))
        
    elif msg == '點名':
        if datetime.date.today().weekday()== 5 :
            line_bot_api.reply_message(reply_token, TextSendMessage(text = recall_78(10)))
        else:
            line_bot_api.reply_message(reply_token, TextSendMessage(text = recall_78(7)))

    elif msg== '清空':
        list_7, list_8, list_10= [], [], []
        ## schedule = '尚無課表'
        line_bot_api.reply_message(reply_token, TextSendMessage(text= '清空!'))
