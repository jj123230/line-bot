
'''
code
'''
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

line_bot_api = LineBotApi(os.environ.get('token'))
handler = WebhookHandler(os.environ.get('secret'))

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
clear.add_job(job,'cron', hour = 22)
clear.start()

def nosleep():
    print('clear!')
    
no_sleep = BackgroundScheduler(daemon=True)
no_sleep.add_job(nosleep,'interval', minute = 20)
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

    
'''
port = 80
import time

import pandas as pd

## Counting and return (Using Dataframe)
def count_list(bot_id, list1, list2, pm):
    if pm == 'plus':
        list1.append(bot_id)
        list2.append(bot_id)
    elif pm == 'minus':
        while bot_id in list1: list1.remove(bot_id)
        while bot_id in list2: list2.remove(bot_id)

def count78():
    global list_7, list_8
    return '7.00: %s人\n8.30: %s人' % (len(set(list_7)), len(set(list_8)))

def count10():
    global list_10
    return '10.30: %s人' % len(set(list_10))


callback= [
    ['7+', list_7, [], 'plus', count78],
    ['7-', list_7, [], 'minus', count78],
    ['8+', list_8, [], 'plus', count78],
    ['8-', list_8, [], 'minus', count78],
    ['10+', list_10, [], 'plus', count10],
    ['10-', list_10, [], 'minus', count10],
    [['78+','7+8+'], list_7, list_8, 'plus', count78],
    [['78-','7-8-'], list_7, list_8, 'minus', count78],
           ]
callback_df = pd.DataFrame(callback,
                           columns=['callback', 'list1', 'list2', 'pm', 'func'])


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

    if status == 'change':
        schedule = msg
        status = 'chat'

    if msg in counting:
        count_list(user_id, 
                   callback_df[(callback_df.callback.apply(lambda x : msg in x))].list1.values[0],
                   callback_df[(callback_df.callback.apply(lambda x : msg in x))].list2.values[0],
                   callback_df[(callback_df.callback.apply(lambda x : msg in x))].pm.values[0])
        time.sleep(1)
        
        reply_text = callback_df[(callback_df.callback.apply(lambda x : msg in x))].func.values[0]()
        line_bot_api.reply_message(reply_token, TextSendMessage(text= reply_text))
        
    elif msg == '指令':
        line_bot_api.reply_message(reply_token, TextSendMessage( \
            text= '教練用: 點名，清空\n學生用: 7+, 8+, 7-, 8-, 78+, 7+8+, 78-, 7-8-, 10+, 10-'))
        
    elif msg == '點名':
        if datetime.date.today().weekday()== 5 :
            line_bot_api.reply_message(reply_token, TextSendMessage(text = count10()))
        else:
            line_bot_api.reply_message(reply_token, TextSendMessage(text = count78()))

    elif msg== '清空':
        list_7, list_8, list_10= [], [], []
        ## schedule = '尚無課表'
        line_bot_api.reply_message(reply_token, TextSendMessage(text= '清空!'))

app.run(port=port)
'''

'''
## API重啟計時器
aps = APScheduler()

@aps.task('cron', id='everyday', day='*', hour='*', minute='*', second='30')
def refresh():
    global list_7, list_8, list_10
    list_7, list_8, list_10 = [], [], []
    print(str(datetime.datetime.now()) + ' everyday')
    
aps.start()

class Config(object):
    SCHEDULER_API_ENABLED = True
    
app.config.from_object(Config())    

aps.init_app(app)
'''

'''
## 加入課表
        keyboard= TextSendMessage(text = '點名',
                                  quick_reply= QuickReply(items= [
            QuickReplyButton(action= PostbackTemplateAction(label= '輸入課表', data = 'enter_schedule')),
            QuickReplyButton(action= PostbackTemplateAction(label= '課表', data = 'schedule')),
            QuickReplyButton(action= PostbackTemplateAction(label= '點名', data = 'count')),
            QuickReplyButton(action= PostbackTemplateAction(label= '清空', data = 'empty'))
            ]))
        line_bot_api.reply_message(reply_token, keyboard)
        
@handler.add(PostbackEvent)
def dscbot_call(event):
    callback = event.postback.data
    user_id = event.source.user_id
    reply_token = event.reply_token
    
    if callback == 'enter_schedule':
        status = 'change'
        line_bot_api.reply_message(reply_token, TextSendMessage(text = '請輸入課表'))
        
    elif callback == 'schedule':
        line_bot_api.reply_message(reply_token, TextSendMessage(text = schedule))
        
    elif callback == 'count':
        time.sleep(1)
        if datetime.date.today().weekday()== 5 :
            line_bot_api.reply_message(reply_token, TextSendMessage(text = count10()))
        else:
            line_bot_api.reply_message(reply_token, TextSendMessage(text = count78()))
            
    elif callback == 'empty':
        global list_7, list_8, list_10 ## schedule, status
        list_7= []
        list_8= []
        list_10= []
        schedule = '尚無課表'
        line_bot_api.reply_message(reply_token, TextSendMessage(text= '清空!'))
        '''
