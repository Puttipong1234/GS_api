from flask import Flask, request, abort
from linebot import (
    LineBotApi, WebhookParser
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, FollowEvent , QuickReply , QuickReplyButton , MessageAction , ImageSendMessage
)

import os
import requests
import json


from Project.Sheet import GSdata

app = Flask(__name__)
from Project.models import Session , db
from Project.connect import create_connection

basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, '{}.sqlite'.format(create_connection('Stock')))


# get channel_secret and channel_access_token from your environment variable
channel_secret = '77c6498f2b89f2df4959f8d21059559c'
channel_access_token = 'Lry+9veBfCmgtFB43jv8ir6wGqNgLw/rA6r89OA+cSAnjyKlighcNjZpwGG2VN0kB2xPn68RwzdiM17AKKPE4kW5OLWpBD+kO2LJ2NpPTZ/x0W5gsNocc1p4j5GL6KJ9tEDZjiPdjGPOz2x1ssawLwdB04t89/1O/w1cDnyilFU='

line_bot_api = LineBotApi(channel_access_token)
parser = WebhookParser(channel_secret)

def send_flex(reply_token,file_data):
    
    LINE_API = 'https://api.line.me/v2/bot/message/reply'

    Authorization = 'Bearer {}'.format(channel_access_token)

    headers = {'Content-Type': 'application/json; charset=UTF-8',
  'Authorization': Authorization}

    file_data['replyToken'] = reply_token
    #### dumps file จาก dict ให้เป็น json
    file_data = json.dumps(file_data)
    r = requests.post(LINE_API, headers=headers, data=file_data) # ส่งข้อมูล

    return 'OK'


@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # parse webhook body
    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        abort(400)

    # if event is MessageEvent and message is TextMessage, then echo text
    for event in events:
        message = 'กรุณากดปุ่มเพื่อเลือกเมนู'

        quick_rep1 = QuickReply(items=[
                                   QuickReplyButton(action=MessageAction(label="รับสินค้า", text="รับสินค้า")),
                                   QuickReplyButton(action=MessageAction(label="จ่ายสินค้า", text="จ่ายสินค้า")),
                                   QuickReplyButton(action=MessageAction(label="ยกเลิกรายการ", text="ยกเลิกรายการ")),
                                   QuickReplyButton(action=MessageAction(label="ไปที่ GoogleSheet", text="ไปที่ GoogleSheet"))
                               ])


        if isinstance(event,MessageEvent):
            if event.message.text == 'รับสินค้า':
                cur_sess = Session.query.get(1)
                cur_sess.session = 'รับสินค้า'
                db.session.commit()
                message = 'กรุณาใส่ รหัสสินค้า / ตามด้วยจำนวนสินค้า / หมายเหตุ(หากมี) ตัวอย่าง EX: 10111/10/สินค้าจากPybott'
                line_bot_api.reply_message(
                    event.reply_token,TextSendMessage(text=message,quick_reply = quick_rep1)
                )
                return '200'

            elif event.message.text == 'จ่ายสินค้า':
                cur_sess = Session.query.get(1)
                cur_sess.session = 'จ่ายสินค้า'
                db.session.commit()
                message = 'กรุณาใส่ รหัสสินค้า / ตามด้วยจำนวนสินค้า / หมายเหตุ(หากมี) ตัวอย่าง EX: 10111/10/สินค้าจากPybott'

                line_bot_api.reply_message(
                    event.reply_token,TextSendMessage(text=message,quick_reply = quick_rep1)
                )
                return '200'
            
            elif Session.query.get(1).session == 'รับสินค้า' :
                user_input = event.message.text.split('/')
                if len(user_input) == 3:
                    GSdata().add_product_data(user_input[1],user_input[0],note = user_input[2])
                else :
                    GSdata().add_product_data(user_input[1],user_input[0])
                cur_sess = Session.query.get(1)
                cur_sess.session = 'none'
                db.session.commit()

                message = 'คุณได้ทำการ รับสินค้าเข้ามา รหัส : {} / จำนวน : {} จัดเก็บเข้าฐานข้อมูลเรียบร้อย'.format(user_input[0],user_input[1])

                line_bot_api.reply_message(
                    event.reply_token,TextSendMessage(text=message,quick_reply = quick_rep1)
                )

                return '200'


            elif Session.query.get(1).session == 'จ่ายสินค้า' :
                user_input = event.message.text.split('/')
                if len(user_input) == 3:
                    GSdata().add_product_data(user_input[1],user_input[0],method = 'จ่าย',note = user_input[2])
                else :
                    GSdata().add_product_data(user_input[1],user_input[0],method = 'จ่าย')
                cur_sess = Session.query.get(1)
                cur_sess.session = 'none'
                db.session.commit()

                message = 'คุณได้ทำการ จ่ายสินค้าออกไป รหัส : {} / จำนวน : {} จัดเก็บเข้าฐานข้อมูลเรียบร้อย'.format(user_input[0],user_input[1])

                line_bot_api.reply_message(
                    event.reply_token,TextSendMessage(text=message,quick_reply = quick_rep1)
                )

                return '200'

            elif event.message.text == 'ยกเลิกรายการ' :
                user_input = event.message.text.split('/')

                message = 'คุณได้ทำการยกเลิกรายการ กรุณาเลือกเมนูใหม่'

                line_bot_api.reply_message(
                    event.reply_token,TextSendMessage(text=message,quick_reply = quick_rep1)
                )
                
                cur_sess = Session.query.get(1)
                cur_sess.session = 'none'
                db.session.commit()
                return '200'

            elif event.message.text == 'สรุปนาฬิกาใคร' :
                
                message = 'ด.ช.ดู่ บริการจัดการสินค้า กรุณาเลือกเมนูได้เลยครับ'
                line_bot_api.reply_message(
                event.reply_token,ImageSendMessage('https://www.khaosod.co.th/wp-content/uploads/2017/12/%E0%B9%84%E0%B8%A1%E0%B9%88%E0%B8%95%E0%B8%AD%E0%B8%9A%E0%B8%99%E0%B8%B0-%E0%B8%99%E0%B8%B2%E0%B8%AC%E0%B8%B4%E0%B8%81%E0%B8%B2%E0%B8%AB%E0%B8%99%E0%B9%88%E0%B8%B0-696x403.jpg','https://www.khaosod.co.th/wp-content/uploads/2017/12/%E0%B9%84%E0%B8%A1%E0%B9%88%E0%B8%95%E0%B8%AD%E0%B8%9A%E0%B8%99%E0%B8%B0-%E0%B8%99%E0%B8%B2%E0%B8%AC%E0%B8%B4%E0%B8%81%E0%B8%B2%E0%B8%AB%E0%B8%99%E0%B9%88%E0%B8%B0-696x403.jpg',quick_rep1)
            )
                return '200'
            
            elif event.message.text == 'ไปที่ GoogleSheet' :
                
                message = 'ด.ช. ตู่ จะนำทางท่านไปที่ GoogleSheet และทำการเปลี่ยนข้อมูลของตาราง ให้เป็นข้อมูล User profile ของท่าน กรุณากด Link https://docs.google.com/spreadsheets/d/1QlhBSROcdRll-tqX3zNaL4KQqIOLlRE0rwIQETNGUC8/edit?usp=sharing'
                line_bot_api.reply_message(
                event.reply_token,TextSendMessage(text=message,quick_reply = quick_rep1)
            )
                return '200'

            elif event.message.text == 'test_01' :
                
                message = ['book','hello']
                line_bot_api.reply_message(
                event.reply_token,TextSendMessage(text=message,quick_reply = quick_rep1)
            )
                return '200'

            elif event.message.text == 'test_02' :
                from Project.flex_data import flex_data
                send_flex(event.reply_token,flex_data)
                
            
                return '200'


            
            else :
                message = 'ยินดีต้อนรับสู่บริการ ด.ช.ดู่ บริการจัดการสินค้า กรุณาเลือกเมนูได้เลยครับ'
                line_bot_api.reply_message(
                event.reply_token,TextSendMessage(text=message,quick_reply = quick_rep1)
            )
                cur_sess = Session.query.get(1)
                cur_sess.session = 'none'
                db.session.commit()
                return '200'




        if isinstance(event,FollowEvent):
            message = 'ยินดีต้อนรับสู่บริการ ด.ช.ดู่ บริการจัดการสินค้า กรุณาเลือกเมนูได้เลยครับ'
            line_bot_api.reply_message(
                event.reply_token,TextSendMessage(text=message,quick_reply = quick_rep1)
            )
            GSdata().update_stock()
            return '200'




