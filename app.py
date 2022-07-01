'''
code
'''
import requests
import re
import time

import pandas as pd
import datetime
import os

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

line_bot_api = LineBotApi(os.environ.get("token"))
handler = WebhookHandler(os.environ.get("secret"))

status = 'chat'

counting = ['7+', '8+', '7-', '8-', '78+', '7+8+', '78-', '7-8-', '10+', '10-']

list_7= []
list_8= []
list_10= []
schedule = '尚無課表'


def count_list(bot_id, list1, list2, pm):
    if pm == 'plus':
        list1.append(bot_id)
        list2.append(bot_id)
    elif pm == 'minus':
        while bot_id in list1: list1.remove(bot_id)
        while bot_id in list2: list2.remove(bot_id)

def count78():
    return '7.00: %s人\n8.30: %s人' % (len(set(list_7)), len(set(list_8)))

def count10():
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


'''
API
'''
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
    msg = event.message.text
    user_id = event.source.user_id
    reply_token = event.reply_token
    
    if status == 'change':
        global schedule
        schedule = msg
    
    if msg in counting:
        list1 = callback_df[(callback_df.callback.apply(lambda x : msg in x))].list1.values[0]
        list2 = callback_df[(callback_df.callback.apply(lambda x : msg in x))].list2.values[0]
        pm = callback_df[(callback_df.callback.apply(lambda x : msg in x))].pm.values[0]
        count_list(user_id, list1, list2, pm)
        
        reply_text = callback_df[(callback_df.callback.apply(lambda x : msg in x))].func.values[0]()
        line_bot_api.reply_message(reply_token, TextSendMessage(text= reply_text))
        
    elif msg == '功能':
        keyboard= TextSendMessage(text = '課表或點名', 
                                  quick_reply= QuickReply(items= [
            QuickReplyButton(action= PostbackTemplateAction(label= '輸入課表', data = 'enter_schedule')),
            QuickReplyButton(action= PostbackTemplateAction(label= '課表', data = 'schedule')),
            QuickReplyButton(action= PostbackTemplateAction(label= '點名', data = 'count'))
            ]))
        line_bot_api.reply_message(reply_token, keyboard)
        
        

@handler.add(PostbackEvent)
def dscbot_call(event):
    callback = event.postback.data
    user_id = event.source.user_id
    reply_token = event.reply_token
    
    if callback == 'enter_schedule':
        global status
        status = 'change'
        line_bot_api.reply_message(reply_token, TextSendMessage(text = '請輸入課表'))
        
    elif callback == 'schedule':
        line_bot_api.reply_message(reply_token, TextSendMessage(text = schedule))
        
    elif callback == 'count':
        if datetime.date.today().weekday()== 5 :
            line_bot_api.reply_message(reply_token, TextSendMessage(text = count10()))
        else:
            line_bot_api.reply_message(reply_token, TextSendMessage(text = count78()))
