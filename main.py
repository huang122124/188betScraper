import logging
import time
from enum import Enum

import LogHelper
import RequestHelper


class FixedType(Enum):
    NONE = 0
    HALF_BLOCKED = 1
    FIXED = 2


class MatchInfo(object):
    def __init__(self, matchId, league, period, minutes, home, home_score, away, away_score):
        self.matchId = matchId
        self.league = league
        self.period = period
        self.minutes = minutes
        self.home = home
        self.home_score = home_score
        self.away = away
        self.away_score = away_score

    def __str__(self):
        return self.league + " " + self.minutes + "' " + " " + self.home + " " + self.home_score + ":" + self.away_score + " " + self.away

    def post_to_tg(self, msg=None):
        if msg is None:
            RequestHelper.post_to_telegram(str(self))
        else:
            RequestHelper.post_to_telegram(msg + str(self))

    def display(self, msg=None):
        if msg is None:
            LogHelper.print_info(str(self))
        else:
            LogHelper.print_info(msg + str(self))


fix_matches = []
inplay_matches = []


def getInplayEvents():
    # json object
    data = RequestHelper.getInplayEvents()
    try:
        # will return false if no soccer live events
        if (data.get('success')):
            leagues = data.get('data').get('seasons')
            parseEvents(leagues)
            check_match_removed()
    except Exception as e:
        LogHelper.print_error(e)


def update_inplay_matches(match_info):
    if match_info not in inplay_matches:
        # need to test the minutes vaule when match end
        if not (match_info.minutes and int(match_info.minutes) > 80):
            inplay_matches.append(match_info)
    else:
        inplay_matches.remove(match_info)


def check_match_removed():
    if len(inplay_matches) > 0:
        for match in inplay_matches:
            match.display("Match Removed:")
            match.post_to_tg("Match Removed:")
        inplay_matches.clear()


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
                    markets = event.get('markets')
                    match_info = MatchInfo(matchId, league_name, period, minutes, home, home_score, away, away_score)
                    # add the match into inplay list
                    update_inplay_matches(match_info)
                    if len(markets) > 0:
                        fixed_type = get_fixed_type(period, minutes, markets)
                        if fixed_type == FixedType.FIXED:
                            if match_info not in fix_matches:
                                fix_matches.append(match_info)
                                match_info.display()
                                match_info.post_to_tg()
                        elif fixed_type == FixedType.HALF_BLOCKED:
                            if match_info not in fix_matches:
                                fix_matches.append(match_info)
                                msg = "Macth half blocked:"
                                match_info.display(msg)
                                match_info.post_to_tg(msg)
                        else:
                            if match_info in fix_matches:
                                fix_matches.remove(match_info)
                            # LogHelper.print_info(
                            #     "Not fixed--->> " + period_text +" "+ minutes + "' " + home + " " + home_score + ":" + away_score + " " + away)


# all params in string
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
