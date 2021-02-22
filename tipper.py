"""
The KickTippTipper logs into your KickTipp account and automatically
submits its generated bets. The bets get calculated by considering
each teams odds.
"""
import json
import math

import werkzeug
from robobrowser import RoboBrowser

werkzeug.cached_property = werkzeug.utils.cached_property

url_login = "https://www.kicktipp.de/info/profil/login"

# Possible Results, modify at will
deuce = [1, 1]
team1_win = [2, 1]
team2_win = [1, 2]
team1_greatwin = [3, 1]
team2_greatwin = [1, 3]


def login():
    """Logs into useraccount"""
    with open('credentials.json') as json_file:
        credentials = json.load(json_file)
    username = credentials['username']
    password = credentials['password']
    browser.open(url_login)
    form = browser.get_form()
    form['kennung'] = username
    form['passwort'] = password
    browser.submit_form(form)

    if not did_login_work():
        print("Your email or password was incorrect. Please try again.")
        print("")


def did_login_work():
    """Returns true if function does not find any input possibility"""
    for i in browser.find_all("input", type="text"):
        if i.get("name") == "kennung":
            return False
    return True


def grab_odds(bet_urls):
    if isinstance(bet_urls, str):
        bet_urls = [bet_urls]
    for url in bet_urls:
        print("Grabbing ods for " + url)
        odds = []
        matchup = []
        gameday = {}
        browser.open(url)
        for i in browser.find_all("td"):
            attributes = i.attrs
            if 'kicktipp-time' in attributes['class']:
                if len(matchup) > 0:
                    gameday[str(matchup)] = {'odds': odds, 'teams': matchup}
                    matchup = []
                    odds = []
                continue
            elif 'kicktipp-wettquote' in attributes['class']:
                quote = float(i.get_text())
                odds.append(quote)
            elif "kicktipp-tippabgabe" in attributes['class']:
                matchup
            else:
                team = i.get_text()
                matchup.append(team)
        gameday[str(matchup)] = {'odds': odds, 'teams': matchup}
    return gameday


def calc_results(odds):
    """By considering odds, calculates match results"""
    print("Calculating Results")
    results = []

    for site in odds:
        sresults = []
        for i in site:
            diff = math.fabs(i[0] - i[2])
            if diff < 1.0:
                sresults.append(deuce)
            elif diff > 8.0:
                if i[0] > i[1]:
                    sresults.append(team2_greatwin)
                else:
                    sresults.append(team1_greatwin)
            else:
                if i[0] > i[1]:
                    sresults.append(team2_win)
                else:
                    sresults.append(team1_win)
        results.append(sresults)
    return results


def get_keys():
    """Get necessary input keys"""
    ret = []
    for url in bet_urls:
        print("Getting input keys for " + url)
        formkeys = []
        browser.open(url)

        for i in browser.find_all("input", type="tel"):
            formkeys.append(i.get("name"))
        formkeys = [formkeys[i:i + 2] for i in range(0, len(formkeys), 2)]
        ret.append(formkeys)
    return ret


def pass_results(bet_urls, results):
    for idx, url in enumerate(bet_urls):
        print("Passing Results to " + url)
        formkeys = get_keys(bet_urls)
        browser.open(url)
        form = browser.get_form()

        # If some matches already have been played the results list needs to be adjusted
        if len(formkeys) != len(results):
            to_delete = len(results[idx]) - len(formkeys)
            results[idx] = results[idx][to_delete:]

        for i in range(0, len(formkeys)):
            form[formkeys[idx][i][0]] = results[idx][i][0]
            form[formkeys[idx][i][1]] = results[idx][i][1]
        browser.submit_form(form)


def grab_kicktipp_groups():
    group_names = []
    for i in browser.find_all("a"):
        link = i.get("href").split("?")[0]
        name = i.contents
        link = link.replace("/", "")
        if link in name:
            group_names.append(link)
    return group_names


def set_bet_urls(links):
    bet_urls = []
    for l in links:
        url_betting.append("https://www.kicktipp.de/" + l + "/tippabgabe")
        url_betting_mobile.append("https://m.kicktipp.de/" + l + "/tippabgabe")



if __name__ == '__main__':
    browser = RoboBrowser(parser="html.parser", history=True)
    login()
    set_bet_urls(grab_beturl())
    my_odds = grab_odds()
    my_results = calc_results(my_odds)
    pass_results(url_betting, my_results)
    print("Done!")
