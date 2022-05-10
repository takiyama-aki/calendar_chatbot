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
import sys
print(sys.path)

app = Flask(__name__)

line_bot_api = LineBotApi('lhqD0fJxzv4nMgoIOdqLeMrTdNTFFaEhI8vX/PBYSDMndxQNRhIVJcTTXM+0txH2IvUDVtHiZpIspqirjCS2mbx0nJ4Gsq4BeB2RIEVHjWTzk/JkXAzuIfiMgzUzmCOIWqoQj66UANRU3xeaYJM1PgdB04t89/1O/w1cDnyilFU=')
#YOUR_CHANNEL_ACCESS_TOKEN
handler = WebhookHandler('03fb497fc092b55b7ce856b2d9b795bd') 
#YOUR_CHANNEL_SECRET

@app.route("/")
def hoge():
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

@app.route("/")
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

        schedule = []
        for g_event in events:
            start = g_event['start'].get('dateTime', g_event['start'].get('date'))
            start = datetime.datetime.strptime(start[:-6], '%Y-%m-%dT%H:%M:%S').strftime('%Y/%m/%d %H:%M')

            end = g_event['end'].get('dateTime', g_event['end'].get('date'))
            end = datetime.datetime.strptime(end[:-6], "%Y-%m-%dT%H:%M:%S").strftime('%H:%M')

            #print(start, g_event['summary'])
            #print(g_event['start'], g_event['end'], g_event['summary'], g_event['description'])
            tmp = "・"+ str(start) + "~" + str(end) +" "+ g_event['summary']
            schedule.append(tmp)

        #print("\n".join(alist))
        reply_txt = "\n\n".join(schedule)
        

    # 明日と言ったら明日の予定を返信する
    if receive_txt == "明日":
        today = datetime.datetime.now().strftime('%Y/%m/%d') # tmp = "年/月/日"
        ymd = today.split("/") # ymd[0]= 年, ymd[1]= 月, ymd[2]= 日 

        tomorrow = datetime.datetime(int(ymd[0]), int(ymd[1]), int(ymd[2]), 15)
        timefrom = tomorrow.isoformat()+'Z'
        timeto = (tomorrow + datetime.timedelta(days= 1)).isoformat()+'Z'

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

            schedule = []
            for g_event in events:
                start = g_event['start'].get('dateTime', g_event['start'].get('date'))
                start = datetime.datetime.strptime(start[:-6], '%Y-%m-%dT%H:%M:%S').strftime('%Y/%m/%d %H:%M')

                end = g_event['end'].get('dateTime', g_event['end'].get('date'))
                end = datetime.datetime.strptime(end[:-6], "%Y-%m-%dT%H:%M:%S").strftime('%H:%M')

                #print(start, g_event['summary'])
                #print(g_event['start'], g_event['end'], g_event['summary'], g_event['description'])
                tmp = "・"+ str(start) + "~" + str(end) +" "+ g_event['summary']
                schedule.append(tmp)

            #print("\n".join(alist))
            reply_txt = "\n\n".join(schedule)
    
    # 指定の日付の予定を取得する
    import re
    if re.fullmatch( r'(\d{2}|\d{1})/(\d{2}|\d{1})',receive_txt):
        tmp = [0, 0, 0]
        tmp[0] = receive_txt[:4]
        tmp[1] = receive_txt[4:6]
        tmp[2] = receive_txt[6:8]
        print(tmp)
        day = datetime.datetime(int(tmp[0]), int(tmp[1]), int(tmp[2])-1, 15)
        print(day)
        

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

            schedule = []
            for g_event in events:
                start = g_event['start'].get('dateTime', g_event['start'].get('date'))
                start = datetime.datetime.strptime(start[:-6], '%Y-%m-%dT%H:%M:%S').strftime('%Y/%m/%d %H:%M')

                end = g_event['end'].get('dateTime', g_event['end'].get('date'))
                end = datetime.datetime.strptime(end[:-6], "%Y-%m-%dT%H:%M:%S").strftime('%H:%M')

                #print(start, g_event['summary'])
                #print(g_event['start'], g_event['end'], g_event['summary'], g_event['description'])
                tmp = "・"+ str(start) + "~" + str(end) +" "+ g_event['summary']
                schedule.append(tmp)

            print("\n".join(schedule))
            reply_txt = "\n\n".join(schedule)
            


    #予定を挿入する
    # "xx/yy hh:mm 予定"
    if re.fullmatch( r'(\d{2}|\d{1})/(\d{2}|\d{1}) (\d{2}|\d{1}):\d{2} [\u0000-\u007F\u3041-\u309F\u30A1-\u30FF\u2E80-\u2FDF\u3005-\u3007\u3400-\u4DBF\u4E00-\u9FFF\uF900-\uFAFF\U00020000-\U0002EBEF]+', receive_txt):
        tmp = receive_txt.split( )
        print(tmp) #tmp[0]: 年 tmp[1]: 時間 tmp[2]: 予定
        year = 2022
        monthday = tmp[0].split("/")
        hourminute = tmp[1].split(":")
        yotei = str(tmp[2])

        eventday = datetime.datetime(int(year), int(monthday[0]), int(monthday[1]), int(hourminute[0]), int(hourminute[1]))
        print(eventday)

        timefrom = eventday.isoformat()
        timeto = (eventday + datetime.timedelta(seconds = 3600)).isoformat()

        g_event = {
            'summary': yotei,
            #'location': 'Shibuya Office',
            #'description': 'サンプルの予定',
            'start': {
                'dateTime': timefrom,
                'timeZone': 'Japan',
            },
            'end': {
                'dateTime': timeto,
                'timeZone': 'Japan',
            },
        }

        g_event = service.events().insert(calendarId='csak19061@g.nihon-u.ac.jp',
                                        body=g_event).execute()
        print (g_event['id'])

        
        reply_txt = "予定を追加しました。"
    
    # "○曜日 予定"
    if re.fullmatch( r'(月|火|水|木|金|土|日)曜日 [\u0000-\u007F\u3041-\u309F\u30A1-\u30FF\u2E80-\u2FDF\u3005-\u3007\u3400-\u4DBF\u4E00-\u9FFF\uF900-\uFAFF\U00020000-\U0002EBEF]+', receive_txt):
        tmp = receive_txt.split()
        youbi = tmp[0][0]
        yotei = tmp[1]
        print(youbi)
        youbitoday = datetime.date.today().weekday()
        
        weekday = 0 if youbi == "月" else 1 if youbi == "火" else 2 if youbi == "水" else 3 if youbi =="木" else 4 if youbi =="金" else 5 if youbi =="土" else 6 if youbi =="日" else None
            
        diff_youbi = weekday - youbitoday

        today = datetime.datetime.now().strftime('%Y/%m/%d')
        ymd = today.split("/") # ymd[0]= 年, ymd[1]= 月, ymd[2]= 日 

        eventday = datetime.datetime(int(ymd[0]), int(ymd[1]), int(ymd[2])+diff_youbi)
        timefrom = eventday.isoformat()+'Z'
        timeto = (eventday + datetime.timedelta(seconds= 3600)).isoformat()+'Z'

        g_event = {
            'summary': yotei,
            #'location': 'Shibuya Office',
            #'description': 'サンプルの予定',
            'start': {
                'dateTime': timefrom,
                'timeZone': 'Japan',
            },
            'end': {
                'dateTime': timeto,
                'timeZone': 'Japan',
            },
        }

        g_event = service.events().insert(calendarId='csak19061@g.nihon-u.ac.jp',
                                        body=g_event).execute()
        print (g_event['id'])

        
        reply_txt = "予定を追加しました。"

    # "来週 ○曜日 予定"
    if re.fullmatch( r'来週 (月|火|水|木|金|土|日)曜日 [\u0000-\u007F\u3041-\u309F\u30A1-\u30FF\u2E80-\u2FDF\u3005-\u3007\u3400-\u4DBF\u4E00-\u9FFF\uF900-\uFAFF\U00020000-\U0002EBEF]+', receive_txt):
        tmp = receive_txt.split()
        youbi = tmp[1][0]
        yotei = tmp[2]
        print(youbi)
        youbitoday = datetime.date.today().weekday()
        
        weekday = 0 if youbi == "月" else 1 if youbi == "火" else 2 if youbi == "水" else 3 if youbi =="木" else 4 if youbi =="金" else 5 if youbi =="土" else 6 if youbi =="日" else None

        diff_youbi = weekday - youbitoday

        today = datetime.datetime.now().strftime('%Y/%m/%d')
        ymd = today.split("/") # ymd[0]= 年, ymd[1]= 月, ymd[2]= 日 

        eventday = datetime.datetime(int(ymd[0]), int(ymd[1]), int(ymd[2])+diff_youbi+7)
        timefrom = eventday.isoformat()+'Z'
        timeto = (eventday + datetime.timedelta(seconds= 3600)).isoformat()+'Z'

        g_event = {
            'summary': yotei,
            #'location': 'Shibuya Office',
            #'description': 'サンプルの予定',
            'start': {
                'dateTime': timefrom,
                'timeZone': 'Japan',
            },
            'end': {
                'dateTime': timeto,
                'timeZone': 'Japan',
            },
        }

        g_event = service.events().insert(calendarId='csak19061@g.nihon-u.ac.jp',
                                        body=g_event).execute()
        print (g_event['id'])

        
        reply_txt = "予定を追加しました。"

    # 返信する
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=reply_txt)) #event.message.text がユーザーが送ってきたテキスト
    
if __name__ == "__main__":
    app.run()