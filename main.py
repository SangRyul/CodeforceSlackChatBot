
import time
import slack as Bot
from slacker import Slacker
from slackclient import SlackClient
import os

# token = os.environ.get('CHATBOTKEY')
token = os.environ.get('CHATBOTKEY')

slack = Slacker(token)
slack_client = SlackClient(token)
flag = False



if __name__ == "__main__":

    READ_WEBSOKET_DELAY = 1
    if slack_client.rtm_connect():
        print("server is running")
        while True:

            command, channel = Bot.parse_slack_output(slack_client.rtm_read())

            if not flag:
                command = "contest"
                channel = "C319P19LJ"
                flag = True


            if command and channel:
                Bot.handle_command(command, channel)

            time.sleep(READ_WEBSOKET_DELAY)
    else:
        print("error")