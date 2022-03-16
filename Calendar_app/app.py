import imp
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


SCOPES = ['https://www.googleapis.com/auth/calendar']

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):

    creds = None
    
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
        #print("token.json exists")
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            print("creds refreshed")
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
            print("Saved the credentials for the next run")

    service = build('calendar', 'v3', credentials=creds)
    receive_txt = event.message.text 
    reply_txt = "あなたは" + receive_txt + "と言った。"

    # 予定と言ったら１週間の予定を返信する。
    if receive_txt == "予定":
        tmp = datetime.datetime.now().strftime('%Y/%m/%d')
        ymd = tmp.split("/")

        today = datetime.datetime(int(ymd[0]), int(ymd[1]), int(ymd[2])-1, 15)
        timefrom = today.isoformat()+'Z'
        timeto = (today + datetime.timedelta(days= 8)).isoformat()+'Z'

        # timefrom = today .strftime('%Y/%m/%d')
        # timeto = (today + datetime.timedelta(weeks= 1)).strftime('%Y/%m/%d')
        # timefrom = datetime.datetime.strptime(timefrom, '%Y/%m/%d').isoformat()+'Z'
        # timeto = datetime.datetime.strptime(timeto, '%Y/%m/%d').isoformat()+'Z'



        events_result = service.events().list(calendarId='csak19061@g.nihon-u.ac.jp',
                                            timeMin=timefrom,
                                            timeMax=timeto,
                                            singleEvents=True,
                                            orderBy='startTime').execute()
        events = events_result.get('items', [])

        print(timefrom, timeto)

        if not events:
            print('No upcoming events found.')
            reply_txt = '予定がないです'
        else:
            reply_txt = '予定があります'

        alist = []
        for g_event in events:
            start = g_event['start'].get('dateTime', g_event['start'].get('date'))
            start = datetime.datetime.strptime(start[:-6], '%Y-%m-%dT%H:%M:%S').strftime('%Y/%m/%d %H:%M')

            end = g_event['end'].get('dateTime', g_event['end'].get('date'))
            end = datetime.datetime.strptime(end[:-6], "%Y-%m-%dT%H:%M:%S").strftime('%H:%M')

            #print(start, g_event['summary'])
            #print(g_event['start'], g_event['end'], g_event['summary'], g_event['description'])
            tmp = "*"+ str(start) + "~" + str(end) +" ["+ g_event['summary']+"]"
            alist.append(tmp)

        #print("\n".join(alist))
        tmp = "\n\n".join(alist)
        reply_txt = tmp

    # 明日と言ったら明日の予定を返信する
    if receive_txt == "明日":
        tmp = datetime.datetime.now().strftime('%Y/%m/%d')  #欲しい日付の１日前の15:00~
        ymd = tmp.split("/")

        tomorrow = datetime.datetime(int(ymd[0]), int(ymd[1]), int(ymd[2]), 15)
        timefrom = tomorrow.isoformat()+'Z'
        timeto = (tomorrow + datetime.timedelta(days= 1)).isoformat()+'Z'


        # timefrom = tomorrow.strftime('%Y/%m/%d')
        # timeto = (tomorrow + datetime.timedelta(days= 1)).strftime('%Y/%m/%d')
        # timefrom = datetime.datetime.strptime(timefrom, '%Y/%m/%d').isoformat()+'Z'
        # timeto = datetime.datetime.strptime(timeto, '%Y/%m/%d').isoformat()+'Z'

        events_result = service.events().list(calendarId='csak19061@g.nihon-u.ac.jp',
                                            timeMin=timefrom,
                                            timeMax=timeto,
                                            singleEvents=True,
                                            orderBy='startTime').execute()
        events = events_result.get('items', [])

        print(timefrom, timeto)
        if not events:
            print('No upcoming events found.')
            reply_txt = '予定がないです'
        else:
            reply_txt = '予定があります'

            alist = []
            for g_event in events:
                start = g_event['start'].get('dateTime', g_event['start'].get('date'))
                start = datetime.datetime.strptime(start[:-6], '%Y-%m-%dT%H:%M:%S').strftime('%Y/%m/%d %H:%M')

                end = g_event['end'].get('dateTime', g_event['end'].get('date'))
                end = datetime.datetime.strptime(end[:-6], "%Y-%m-%dT%H:%M:%S").strftime('%H:%M')

                #print(start, g_event['summary'])
                #print(g_event['start'], g_event['end'], g_event['summary'], g_event['description'])
                tmp = "*"+ str(start) + "~" + str(end) +" ["+ g_event['summary']+"]"
                alist.append(tmp)

            #print("\n".join(alist))
            tmp = "\n\n".join(alist)
            reply_txt = tmp
    
    # 指定の日付の予定を取得する
    import re
    if re.fullmatch( r'\d{4}/\d{2}/\d{2}',receive_txt):
        tmp = receive_txt.split("/")
        print(tmp)
        day = datetime.datetime(int(tmp[0]), int(tmp[1]), int(tmp[2])-1, 15)
        print(day)
        
        # timefrom = day.strftime('%Y/%m/%d')
        # timeto = (day + datetime.timedelta(days= 1)) .strftime('%Y/%m/%d')
        # timefrom = datetime.datetime.strptime(timefrom, '%Y/%m/%d').isoformat()+'Z'
        # timeto = datetime.datetime.strptime(timeto, '%Y/%m/%d').isoformat()+'Z'

        timefrom = day.isoformat()+'Z'
        timeto = (day + datetime.timedelta(days= 1)).isoformat()+'Z'

        print("timefrom: ",timefrom," timeto: ", timeto)

        events_result = service.events().list(calendarId='csak19061@g.nihon-u.ac.jp',
                                            timeMin=timefrom,
                                            timeMax=timeto,
                                            singleEvents=True,
                                            orderBy='startTime').execute()
        events = events_result.get('items', [])

        
        if not events:
            print('No upcoming events found.')
            reply_txt = '予定がないです'
        else:
            reply_txt = '予定があります'

            alist = []
            for g_event in events:
                start = g_event['start'].get('dateTime', g_event['start'].get('date'))
                start = datetime.datetime.strptime(start[:-6], '%Y-%m-%dT%H:%M:%S').strftime('%Y/%m/%d %H:%M')

                end = g_event['end'].get('dateTime', g_event['end'].get('date'))
                end = datetime.datetime.strptime(end[:-6], "%Y-%m-%dT%H:%M:%S").strftime('%H:%M')

                #print(start, g_event['summary'])
                #print(g_event['start'], g_event['end'], g_event['summary'], g_event['description'])
                tmp = "*"+ str(start) + "~" + str(end) +" ["+ g_event['summary']+"]"
                alist.append(tmp)

            print("\n".join(alist))
            tmp = "\n\n".join(alist)
            reply_txt = tmp

        
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply_txt)) #event.message.text がユーザーが送ってきたテキスト

    import pickle

    #予定を挿入する
    if receive_txt == "挿入":
        
        event = {
            'summary': '予定1',
            'location': 'Shibuya Office',
            'description': 'サンプルの予定',
            'start': {
                'dateTime': '2022-03-20T09:00:00',
                'timeZone': 'Japan',
            },
            'end': {
                'dateTime': '2022-03-20T17:00:00',
                'timeZone': 'Japan',
            },
        }

        event = service.events().insert(calendarId='csak19061@g.nihon-u.ac.jp',
                                        body=event).execute()
        print (event['id'])
    
if __name__ == "__main__":
    app.run()