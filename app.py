# -*- coding: utf-8 -*-


bot_type = 'ln'

line_channel_secret = 'cc1d8b57614278cab126252aa4610364'
line_token = 'H4IKf9kD11BsYCvNFaKoHvxb4LCnbt90RhTqpbvamFpdOHkpplrK/pN+yJ/hKtZujU8tVAA64VZ2ZHP2nZgtHELCDrRK'+\
    'BdjsNMrBmOvaqKmAldGuLl/YgsCAaJFKJNs/2aU/nMM6c9kNyhjm+6XIMAdB04t89/1O/w1cDnyilFU='

port_ip = 80  ## 需更改IP 

'''
code
'''
import requests
import re
import time

import pandas as pd
from datetime import datetime
import urllib.request

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

line_bot_api = LineBotApi(line_token)
handler = WebhookHandler(line_channel_secret)

stat_df = pd.DataFrame(columns=['bot', 'bot_id', 'standard', 'peanut'])

def check_status(bot, bot_id, callback):
    global stat_df
    try:
        standard = stat_df[(stat_df.bot == bot) & (stat_df.bot_id == bot_id)].standard.values[0]
        peanut = stat_df[(stat_df.bot == bot) & (stat_df.bot_id == bot_id)].peanut.values[0]
        
    except Exception:
        stat_df = stat_df.append({"bot" : bot,
                                  "bot_id" : bot_id, 
                                  "standard" : 0,
                                  "peanut" : 0}, 
                                     ignore_index=True)
        standard = 0
        peanut = 0
        
    if callback == 'standard_minus':
        stat_df.at[stat_df[(stat_df.bot == bot) & (stat_df.bot_id == bot_id)].index[0], 'standard'] = standard - 1
    elif callback == 'standard_plus':
        stat_df.at[stat_df[(stat_df.bot == bot) & (stat_df.bot_id == bot_id)].index[0], 'standard'] = standard + 1
    elif callback == 'peanut_minus':
        stat_df.at[stat_df[(stat_df.bot == bot) & (stat_df.bot_id == bot_id)].index[0], 'peanut'] = peanut - 1
    elif callback == 'peanut_plus':
        stat_df.at[stat_df[(stat_df.bot == bot) & (stat_df.bot_id == bot_id)].index[0], 'peanut'] = peanut + 1
    elif callback == 'empty':
        stat_df.at[stat_df[(stat_df.bot == bot) & (stat_df.bot_id == bot_id)].index[0], 'standard'] = 0
        stat_df.at[stat_df[(stat_df.bot == bot) & (stat_df.bot_id == bot_id)].index[0], 'peanut'] = 0
        
    standard = stat_df[(stat_df.bot == bot) & (stat_df.bot_id == bot_id)].standard.values[0]
    peanut = stat_df[(stat_df.bot == bot) & (stat_df.bot_id == bot_id)].peanut.values[0]
        
    return standard, peanut


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
    
    if msg in ['送出訂單', '清空購物車']:
        flex = FlexSendMessage(
            alt_text= ' 前往官網',
            contents = {
                      "type": "bubble",
                      "hero": {
                        "type": "image",
                        "url": "https://imgur.com/aZcJH5H.jpg#",
                        "size": "full",
                        "aspectRatio": "20:13",
                        "aspectMode": "cover",
                        "action": {
                          "type": "uri",
                          "uri": "https://www.xn--phtz3i6te2s4ax8g038a4oh.tw/about-us.html"
                        }
                      }
                    })
        line_bot_api.reply_message(reply_token, flex)
        
    else:
        line_bot_api.reply_message(reply_token, TextSendMessage(text= msg))

@handler.add(PostbackEvent)
def dscbot_call(event):
    callback = event.postback.data
    user_id = event.source.user_id
    reply_token = event.reply_token
    
    ## Image Map
    if callback == 'peanut_image':
        image_message = ImageSendMessage(
            original_content_url= 'https://imgur.com/aZcJH5H.jpg#',
            preview_image_url = 'https://imgur.com/aZcJH5H.jpg#'
            )
        line_bot_api.reply_message(reply_token, image_message)
        
    elif callback == 'standard_image':
        image_message = ImageSendMessage(
            original_content_url= 'https://imgur.com/HfndbfZ.jpg#', ## standard
            preview_image_url = 'https://imgur.com/HfndbfZ.jpg#', ## standard
            )
        line_bot_api.reply_message(reply_token, image_message)
        
    elif callback in ['standard_minus', 'standard_plus', 'peanut_minus', 'peanut_plus']:
        standard, peanut = check_status(bot_type, user_id, callback)
        
        keyboard= TextSendMessage(text = '您的購物車裡目前為 \n招牌麻糬: %s盒\n花生麻糬: %s盒' % (standard, peanut), 
                                  quick_reply= QuickReply(items= [
            QuickReplyButton(action= PostbackTemplateAction(label= '清空購物車', text='清空購物車', data = 'empty')),
            QuickReplyButton(action= PostbackTemplateAction(label= '送出訂單', text='送出訂單', data = 'send'))
            ]))
        line_bot_api.reply_message(reply_token, keyboard)
        
    elif callback == 'empty':
        check_status(bot_type, user_id, callback)
        line_bot_api.reply_message(reply_token, TextSendMessage(text = '購物車已清空，歡迎下次再來採購'))
        
    elif callback == 'send':
        standard, peanut = check_status(bot_type, user_id, callback)
        line_bot_api.reply_message(reply_token, 
                                   TextSendMessage(text = '送出訂單:\n招牌麻糬: %s盒\n花生麻糬: %s盒\n感謝訂購!' % (standard, peanut)))



## app.run(port= port_ip)
