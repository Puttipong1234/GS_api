from flask import Flask, request, abort
from linebot import (
    LineBotApi, WebhookParser
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage, FollowEvent , QuickReply , QuickReplyButton , MessageAction
)

import os


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
                db.session.add(Session('รับสินค้า'))
                db.session.commit()
                message = 'กรุณาใส่ รหัสสินค้า / ตามด้วยจำนวนสินค้า / หมายเหตุ(หากมี) ตัวอย่าง EX: 10111/10/สินค้าจากPybott'
                line_bot_api.reply_message(
                    event.reply_token,TextSendMessage(text=message,quick_reply = quick_rep1)
                )
                return 200

            elif event.message.text == 'จ่ายสินค้า':
                db.session.add(Session('จ่ายสินค้า'))
                db.session.commit()
                message = 'กรุณาใส่ รหัสสินค้า / ตามด้วยจำนวนสินค้า / หมายเหตุ(หากมี) ตัวอย่าง EX: 10111/10/สินค้าจากPybott'
                line_bot_api.reply_message(
                    event.reply_token,TextSendMessage(text=message,quick_reply = quick_rep1)
                )
                return 200
            
            elif Session.query.first() == 'รับสินค้า' :
                user_input = event.message.text.split('/')
                if len(user_input) == 3:
                    GSdata().add_product_data(user_input[1],user_input[0],note = user_input[2])
                else :
                    GSdata().add_product_data(user_input[1],user_input[0])
                db.session.delete(Session.query.first())
                db.session.commit()
                return 200
            elif Session.query.first() == 'จ่ายสินค้า' :
                user_input = event.message.text.split('/')
                if len(user_input) == 3:
                    GSdata().add_product_data(user_input[1],user_input[0],method = 'จ่าย',note = user_input[2])
                else :
                    GSdata().add_product_data(user_input[1],user_input[0],method = 'จ่าย')
                db.session.delete(Session.query.first())
                db.session.commit()
                return 200

            elif event.message.text == 'ยกเลิกรายการ' :
                user_input = event.message.text.split('/')
                
                db.session.delete(Session.query.first())
                db.session.commit()
                return 200


        if isinstance(event,FollowEvent):
            message = 'ยินดีต้อนรับสู่บริการ ด.ช.ดู่ บริการจัดการสินค้า กรุณาเลือกเมนูได้เลยครับ'
            line_bot_api.reply_message(
                event.reply_token,TextSendMessage(text=message,quick_reply = quick_rep1)
            )
            return 200


    