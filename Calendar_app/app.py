from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)

app = Flask(__name__)

line_bot_api = LineBotApi('lhqD0fJxzv4nMgoIOdqLeMrTdNTFFaEhI8vX/PBYSDMndxQNRhIVJcTTXM+0txH2IvUDVtHiZpIspqirjCS2mbx0nJ4Gsq4BeB2RIEVHjWTzk/JkXAzuIfiMgzUzmCOIWqoQj66UANRU3xeaYJM1PgdB04t89/1O/w1cDnyilFU=')
#YOUR_CHANNEL_ACCESS_TOKEN
handler = WebhookHandler('03fb497fc092b55b7ce856b2d9b795bd') 
#YOUR_CHANNEL_SECRET

@app.route("/")
def test():
    return "OK"
    
@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'

import os.path
import datetime

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.errors import HttpError
from googleapiclient.discovery import build


SCOPES = ['https://www.googleapis.com/auth/calendar.readonly']

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):

    creds = None
    
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        print("token.json exists")
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            print("creds refreshed")
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
            print("beroberobar")
        # Save the credentials for the next run
        
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
            print("Saved the credentials for the next run")

    service = build('calendar', 'v3', credentials=creds)
    now = datetime.datetime.utcnow().isoformat() + 'Z'

    receive_txt = event.message.text 
    reply_txt = "あなたは" + receive_txt + "と言った。"

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply_txt)) #event.message.text がユーザーが送ってきたテキスト

    
if __name__ == "__main__":
    app.run()