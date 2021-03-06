#! /usr/local/bin/python3
# -*- coding: utf-8 -*-

import datetime
import os
import socket
import threading
import time
import json

from src.net.createtalk import CreateTalk, pygame_alert
from src.net.createtalk import print_log
from src.net.newscheck import NewsCheck
from src.net.weathercheck import WeatherCheck


class WatcherApi:
    def __init__(self, port=6789):
        ip_list = []
        for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]:
            try:
                s.connect(('8.8.8.8', 80))
            except:
                print('Network is unreachable')
                os._exit(1)

            ip = s.getsockname()
            for n in ip:
                name = ip[0]
                ip_list.append(name)
            s.close()

        self.stop_event = False
        self.server_info = ('127.0.0.1', port)
        self.MAX_SIZE = 1024

        self.ALARM_START_HOUR = 23
        self.ALARM_START_MINUTE = 29
        self.ALARM_REPEAT_INTERVAL = 30
        self.ALARM_REPEAT_COUNT = 4

        threading.Thread(target=self.server_start).start()
        os.chdir(os.path.dirname(os.path.abspath(__file__)))
        print('Starting watcher')
        for now in iter(datetime.datetime.today, ()):
            self.stop_event = False
            if now.hour == self.ALARM_START_HOUR and now.minute == self.ALARM_START_MINUTE:
                self.alarm_start()
                time.sleep(self.ALARM_REPEAT_INTERVAL * 60)
            time.sleep(30)

    def alarm_start(self):
        if not self.stop_event:
            for i in range(self.ALARM_REPEAT_COUNT):
                if not self.stop_event:
                    today = datetime.datetime.today().strftime('%Y_%m_%d_%H_%M_%S')

                    DIR_NAME = 'log/data/' + today

                    weather_check = WeatherCheck()
                    news_check = NewsCheck()

                    weekday = ['月曜日', '火曜日', '水曜日', '木曜日', '金曜日', '土曜日', '日曜日']
                    date_talk = datetime.datetime.today().strftime('%Y年%m月%d日') + '、' + weekday[
                        datetime.date.today().weekday()] + 'です。'
                    weather_talk = '今日の天気は、' + weather_check.get_today_weather() + 'です。'
                    temp_talk = '最高気温は、' + weather_check.get_temp('max') + '。' + '最低気温は、' + weather_check.get_temp(
                            'min') + 'です。'
                    rss_news_talk = '今日の主要なニュース。ひとつ目は、' + news_check.get_rss_news_title(1) + '。次に、'\
                                    + news_check.get_rss_news_title(2)
                    rss_news_talk_2 = '。次に、' + news_check.get_rss_news_title(3) + '。最後に、' \
                                + news_check.get_rss_news_title(4) + '。以上です。'

                    filename_weather = 'weather.wav'
                    filename_news_1 = 'news.wav'
                    filename_news_2 = 'news2.wav'

                    speaker = 'hikari'

                    CreateTalk.create_talk(date_talk + weather_talk + temp_talk, filename_weather, DIR_NAME, speaker=speaker)
                    CreateTalk.create_talk(rss_news_talk, filename_news_1, DIR_NAME, speaker=speaker)
                    CreateTalk.create_talk(rss_news_talk_2, filename_news_2, DIR_NAME, speaker=speaker)

                    @print_log
                    @pygame_alert
                    def talk():
                        if not self.stop_event:
                            CreateTalk.pygame_speak(filename_weather, DIR_NAME)
                            time.sleep(1)
                        if not self.stop_event:
                            CreateTalk.pygame_speak(filename_news_1, DIR_NAME)
                            time.sleep(1)
                        if not self.stop_event:
                            CreateTalk.pygame_speak(filename_news_2, DIR_NAME)

                    talk()

        self.stop_event = False
        print('-- watcher is the end --')

    def server_start(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            server.bind(self.server_info)
        except:
            print('Address already in use')
            os._exit(1)

        STOP_ALARM = 0
        JSON_DUMPS_ERROR = 100

        print('Starting the server at', datetime.datetime.now())
        print('Waiting for a client to call.')
        while True:
            server.listen(5)
            client, address = server.accept()
            data = client.recv(self.MAX_SIZE)
            print('At', datetime.datetime.now(), client)

            try:
                client_message = json.loads(data.decode('UTF-8'))
            except:
                client_message = {'flag':''}
            
            print('client massage number : ' + str(client_message['flag']))
            
            if client_message['flag'] == STOP_ALARM:
                self.stop_event = True
                client.sendall(json.dumps({'flag': STOP_ALARM}).encode('utf-8'))
            elif client_message['flag'] == JSON_DUMPS_ERROR:
                client.sendall(json.dumps({'flag': JSON_DUMPS_ERROR}).encode('utf-8'))
            client.close()
        server.close()

        print('Reset connection')

if __name__ == '__main__':
    a = WatcherApi(6789)

    #プロトコルバッファー

