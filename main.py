import logging
import time
from enum import Enum

import LogHelper
import RequestHelper


class FixedType(Enum):
    NONE = 0
    HALF_BLOCKED = 1
    FIXED = 2


fix_matches = []


def getInplayEvents():
    # json object
    data = RequestHelper.getInplayEvents()
    try:
        # will return false if no soccer live events
        if (data.get('success')):
            leagues = data.get('data').get('seasons')
            parseEvents(leagues)
    except Exception as e:
        LogHelper.print_error(e)


def parseEvents(leagues):
    if (leagues and len(leagues) > 0):
        for league in leagues:
            league_name = league.get('name')
            matches = league.get('matches')
            if (len(matches) > 0):
                for event in matches:
                    matchId = event.get('matchId')
                    period = event.get('liveStatus')
                    period_text = event.get('liveStatusText')
                    minutes = str(event.get('clock')).split(':')[0]
                    totalMarkets = event.get('totalMarkets')
                    home = event.get('competitors').get('home').get('name')
                    home_score = str(event.get('competitors').get('home').get('score'))
                    away = event.get('competitors').get('away').get('name')
                    away_score = str(event.get('competitors').get('away').get('score'))
                    # -------------------------
                    markets = event.get('markets')
                    if len(markets) > 0 and minutes != "":
                        fixed_type = get_fixed_type(period, minutes, markets)
                        if fixed_type == FixedType.FIXED:
                            if matchId not in fix_matches:
                                fix_matches.append(matchId)
                                msg = league_name + " " + minutes + "' " + " " + home + " " + home_score + ":" + away_score + " " + away
                                LogHelper.print_info(msg)
                                RequestHelper.post_to_telegram(msg)
                        elif fixed_type == FixedType.HALF_BLOCKED:
                            if matchId not in fix_matches:
                                fix_matches.append(matchId)
                                msg = "Macth half blocked:" + league_name + " " + minutes + "' " + home + " " + home_score + ":" + away_score + " " + away
                                LogHelper.print_info(msg)
                                RequestHelper.post_to_telegram(msg)
                        else:
                            pass
                            # LogHelper.print_info(
                            #     "Not fixed--->> " + period_text +" "+ minutes + "' " + home + " " + home_score + ":" + away_score + " " + away)


def get_fixed_type(period, minutes, markets):
    available_ah = False
    available_ou = False
    available_half = False  # False when half market not exist
    available_others = False
    other_list = []
    for market in markets:
        name = market.get('header')
        if name == '让球':
            available_ah = is_available(market)
        elif name == '进球: 大 / 小':
            available_ou = is_available(market)
        elif name == '让球-上半场' or name == '进球: 大 / 小-上半场':
            available_half = True
        else:
            other_list.append(is_available(market))
    if True in other_list:
        available_others = True
    if period == 'HT' and (available_ah or available_ou) and not available_others:
        return FixedType.FIXED
    if int(minutes) > 3:
        if period == '1H' and int(minutes) < 40:
            if (available_ah or available_ou) and not available_half:
                return FixedType.HALF_BLOCKED
        if int(minutes) < 80 and (available_ah or available_ou) and not available_others:
            return FixedType.FIXED
    return FixedType.NONE


def is_available(market):
    return market.get('outcomes')[0].get('status') == 'available'


if __name__ == '__main__':
    LogHelper.print_info("start....")
    while True:
        getInplayEvents()
        time.sleep(3)
