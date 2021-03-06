# -*- coding: utf-8 -*-
"""
Created on Sun Jul  9 17:15:22 2017
@author: ksl97
"""

import requests, json
import datetime
from slacker import Slacker
from slackclient import SlackClient
import operator
import os

token = os.environ.get('CHATBOTKEY')


slack = Slacker(token)
slack_client = SlackClient(token)
AT_BOT = "forcebot"



def alert():
    url = "http://codeforces.com/api/contest.list"
    res = requests.get(url=url)
    data = json.loads(res.text)
    
    send_messages = "<*- Upcoming Contest list *->\n"
    
    # for x in range(len(data["result"])):
    for x in range(20): #heuristic
        if(data["result"][x]["phase"] == "BEFORE"):
            #send_messages += data["result"][x]["phase"] + '\n'
            send_messages += data["result"][x]["name"] + '\n'
            
            #during time
            during_time = data["result"][x]["durationSeconds"]
            during_time =str(int(during_time)/3600)
            during_time +=" 시간 동안 진행합니다 \n"
            
            #unix time change
            real_time = data["result"][x]["startTimeSeconds"]
            real_time = datetime.datetime.fromtimestamp(real_time).strftime('%Y-%m-%d %H:%M:%S')
            real_time +=" 에 시작합니다 \n"
            
            get_now_time = data["result"][x]["relativeTimeSeconds"]
            get_now_time = int(abs(get_now_time))
            
            m , s = divmod(get_now_time, 60)
            h, m = divmod(m, 60)
            d, h = divmod(h, 24)
            now_time = str(d)
            now_time += "일 "
            now_time += ("%d 시간 %d 분 %d 초" %(h, m, s))
            now_time +=" 남았습니다 \n"
            
            
            send_messages += str(real_time)
            send_messages += str(now_time)
            send_messages += str(during_time)
            
            send_messages+="------------------------------------------\n"
            
    return send_messages
    
def helpmsg():
    tmpmsg = "Made by Kerafyrm(SangRyul) \n " \
             "ping: Check whether server is alive \n " \
             "contest: Get upcoming codeforces contest information \n" \
             "user <nickname>: Get <nickname>'s info ex) forcebot user kerafyrm \n" \
             "addlist <nickname>: Add local competition list ex) forcebot addlist kerafyrm  \n" \
             "showlist : Show local competiton list  \n" \

    return tmpmsg

def getUserInfo(user):
    url = "http://codeforces.com/api/user.info"
    payload = {'handles': user}
    res = requests.get(url=url, params = payload)
    data = json.loads(res.text)
    send_messages = user + " 님의 정보입니다. \n"
    image_url = ""

    print(data)
    if(data['status'] == 'FAILED'):
        return ["잘못된 유저 이름입니다.",""]

    try:
        send_messages += ("소속  :  " + str(data['result'][0]['organization']) + '\n')
        send_messages += ("국가  :  " + str(data['result'][0]['country']) + '\n')
        send_messages += ("도시  :  " + str(data['result'][0]['city']) + '\n')
        send_messages += ("랭크  :  " + str(data['result'][0]['rank']) +'\n')
        send_messages += ("레이팅  :  " + str(data['result'][0]['rating']) + '\n')
        send_messages += ("최대 랭크  :  " + str(data['result'][0]['maxRank']) + '\n')
        send_messages += ("최대 레이팅  :  " + str(data['result'][0]['maxRating']) + '\n')
        image_url = str(data['result'][0]['titlePhoto'])
    except:
        send_messages += ("랭크  :  " + str(data['result'][0]['rank']) +'\n')
        send_messages += ("레이팅  :  " + str(data['result'][0]['rating']) + '\n')
        send_messages += ("최대 랭크  :  " + str(data['result'][0]['maxRank']) + '\n')
        send_messages += ("최대 레이팅  :  " + str(data['result'][0]['maxRating']) + '\n')
        image_url = str(data['result'][0]['titlePhoto'])


    return [send_messages, image_url]

def setUserInfo(user):

    f = open("userlist.txt", 'a')
    f.write(user+'\n')
    f.close()

    return user + "님 경쟁리스트에 추가되었습니다."

def showList():
    f = open("userlist.txt", 'r')

    text = "< CAUCHAOS 경쟁리스트 >"
    list_set = []
    while True:
        line = f.readline()
        if not line : break
        list_set.append(line)
        list_set =  list(set(list_set))

    f.close()

    query_string = ""
    for x in list_set:
        query_string += x
        query_string += ";"

    url = "http://codeforces.com/api/user.info"
    payload = {'handles': query_string}
    res = requests.get(url=url, params = payload)
    data = json.loads(res.text)

    competition_list = []
    for x in data['result']:
        competition_list.append((x["handle"] , x["rating"]))

    competition_list = sorted(competition_list, key=lambda val : val[1], reverse=True)

    data = "-< Competiton list >-\n\n"
    i = 1
    for x in competition_list:
        data += (str(i)+"등  " + str(x[0]) + " : " + str(x[1]) + " 점 \n")
        i += 1
    return data




def parse_slack_output(slack_rtm_output):
    #메세지 읽어들여서 bot에세 보내는지 안보내는지 확인
    output_list = slack_rtm_output
    if output_list and len(output_list) > 0:
        for output in output_list:
            if output and 'text' in output and AT_BOT in output['text']:
                # return text after the @ mention, whitespace removed
                return output['text'].split(AT_BOT)[1].strip().lower(), \
                       output['channel']
    return None, None

def handle_command(command, channel):

    params = "" #additional parameter
    if(len(command.split(" ")) == 2):
        params = command.split(" ")[1]

    response = ""
    attachments = ""

    if command.startswith("contest"):
        response = alert()
    elif command.startswith("ping"):
        response = "pong"
    elif command.startswith("help"):
        response = helpmsg()
    elif command.startswith("user"):
        response, image_url = getUserInfo(params)
        attachments= [{
            "title": params,
            "title_link": 'http://codeforces.com/profile/' + params,
            "image_url" : image_url
        }]
    elif command.startswith("addlist"):
        response = setUserInfo(params)
    elif command.startswith('showlist'):
        response = showList()



    slack_client.api_call("chat.postMessage", channel=channel,attachments = attachments, text=response, as_user=True)

