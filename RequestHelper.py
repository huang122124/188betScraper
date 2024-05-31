import json
import urllib.parse

import requests
import os
from proxy_seller_user_api import Api
from requests.adapters import HTTPAdapter
from requests.auth import HTTPProxyAuth

import ConfigLoader
import LogHelper

s = requests.Session()
s.mount('http://', HTTPAdapter(max_retries=5))
s.mount('https://', HTTPAdapter(max_retries=5))

def getInplayEvents():
    return s.get(url = ConfigLoader.get('BOYING_MENU_ODDS_URL'),headers={'Referer':'https://v66588.app/','User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36'}).json()
def post_to_telegram(message):
    # 1394697259:AnmvWtkhc8@45.206.50.210:50100'
    response = s.post(url=ConfigLoader.get('TG_URL'), params={
        'chat_id': ConfigLoader.get('CHAT_ID'),
        'text': message
    }, proxies={'http':'127.0.0.1:7890','https':'127.0.0.1:7890'},timeout=20)
    if response.status_code != 200:
        LogHelper.print_error("post_to_telegram failed: "+str(response.text))

if __name__ == '__main__':
    getInplayEvents()
    post_to_telegram("111")