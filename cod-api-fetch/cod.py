#!/usr/bin/env python
from __future__ import print_function

from uuid import uuid4
import requests
import hashlib
import json


DEFAULT_BASE_URL = "https://my.callofduty.com/api/papi-client/"
COD_ENDPOINTS = {
    'all': {
        'MWLeaderboard': 'leaderboards/v2/title/mw/platform/{platform}/time/alltime/type/core/mode/career/page/1'
    },
    'user': {
        'combatmp': "crm/cod/v2/title/mw/platform/{platform}/gamer/{userid}/matches/mp/start/{startdate}/end/{enddate}/details",
        'combatwz': "crm/cod/v2/title/mw/platform/{platform}/gamer/{userid}/matches/wz/start/{startdate}/end/{enddate}/details",
        'fullcombatmp': "crm/cod/v2/title/mw/platform/{platform}/gamer/{userid}/matches/mp/start/{startdate}/end/{enddate}",
        'fullcombatwz': "crm/cod/v2/title/mw/platform/{platform}/gamer/{userid}/matches/wz/start/{startdate}/end/{enddate}",
        'mp': "stats/cod/v1/title/mw/platform/{platform}/gamer/{userid}/profile/type/mp",
        'wz': "stats/cod/v1/title/mw/platform/{platform}/gamer/{userid}/profile/type/wz",
        'mpfriends': "stats/cod/v1/title/mw/platform/{platform}/gamer/{userid}/profile/friends/type/mp",
        'wzfriends': "stats/cod/v1/title/mw/platform/{platform}/gamer/{userid}/profile/friends/type/wz",
        'mpstats': 'stats/cod/v1/title/mw/platform/{platform}/gamer/{userid}/profile/type/mp',
        'wzstats': 'stats/cod/v1/title/mw/platform/{platform}/gamer/{userid}/profile/type/wz',
        'loot': "loot/title/mw/platform/{platform}/gamer/{userid}/status/en",
        'analysis': "ce/v2/title/mw/platform/{platform}/gametype/all/gamer/{userid}/summary/match_analysis/contentType/full/end/0/matchAnalysis/mobile/en",
        'codpoints': "inventory/v1/title/{title}/platform/{platform}/gamer/{userid}/currency"
    }
}


class CallOfDutyAPIClient(object):
    deviceId = None
    ssoCookie = None
    cookies = {
        'new_SiteId': 'cod',
        'ACT_SSO_LOCALE': 'en_US',
        'country': 'US',
        'XSRF-TOKEN': '68e8b62e-1d9d-4ce1-b93f-cbe5ff31a041',
        'API_CSRF_TOKEN': '68e8b62e-1d9d-4ce1-b93f-cbe5ff31a041'
    }
    userAgent = ""
    loggedIn = False
    debug = False

    platforms = {
        "battle": "battle",
        "steam": "steam",
        "psn": "psn",
        "xbl": "xbl",
        "acti": "uno",
        "uno": "uno"
    }

    # http
    headers = {
        "Content-Type": "application/json",
        "Cookie": ";".join(["=".join([x,y]) for x,y in cookies.items()]),
        "User-Agent": userAgent,
        "x-requested-with": userAgent,
        "Accept": "application/json, text/javascript, */*; q=0.01",
        "Connection": "keep-alive"
    }

    # urls
    defaultBaseURL = "https://my.callofduty.com/api/papi-client/"
    loginURL = "https://profile.callofduty.com/cod/mapp/"
    defaultProfileURL = "https://profile.callofduty.com/"
    modernwarfare = "mw"


    def __init__(self, platform="battle", debug=False, ratelimit=None):
        self.platform = platform
        self.debug = debug
        self.ratelimit = ratelimit

    def login(self, email, password):
        randomId = str(uuid4()).encode()
        md5sum = hashlib.md5(randomId)
        deviceId = md5sum.hexdigest()

        data = {"deviceId": deviceId}
        response = requests.post(self.loginURL + "registerDevice", headers=self.headers, json=data)
        response.raise_for_status()
        data = response.json()
        if data['status'] != 'success':
            raise Exception("could not register new device id")

        authHeader = data['data']['authHeader']
        self.headers['Authorization'] = 'Bearer %s' % authHeader
        self.headers['x_cod_device_id'] = deviceId

        data = {"email": email, "password": password}
        response = requests.post(self.loginURL + 'login', headers=self.headers, json=data)
        response.raise_for_status()
        data = response.json()
        if data['success'] is False:
            raise Exception("could not log in")
        
        self.ssoCookie = data['s_ACT_SSO_COOKIE']
        self.cookies['rtkn'] = data['rtkn']
        self.cookies['ACT_SSO_COOKIE'] = data['s_ACT_SSO_COOKIE']
        self.cookies['atkn'] = data['atkn']

        self.headers['Cookie'] = ";".join(["=".join([x,y]) for x,y in self.cookies.items()])
        
        self.loggedIn = True
        return True
        
    def sendRequest(self, baseURL, path, method="GET", data=None):
        if not self.loggedIn:
            raise Exception("Not logged in")
        
        endpoint = baseURL + path
        headers = self.headers

        if method == 'GET': 
            response = requests.get(endpoint, headers=headers, cookies=self.cookies, params=data)
        elif method == 'POST': 
            response = requests.post(endpoint, headers=headers, cookies=self.cookies, json=data)
        elif method == 'PUT':
            response = requests.put(endpoint, headers=headers, cookies=self.cookies, json=data)

        response.raise_for_status()
        data = response.json()
        if not data['status'] == "success":
            raise Exception("API call failed - %s" % data)

        return data
        

