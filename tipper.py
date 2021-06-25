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


def login(robo_browser):
    """Logs into useraccount"""
    with open('credentials.json') as json_file:
        credentials = json.load(json_file)
    username = credentials['username']
    password = credentials['password']
    robo_browser.open(url_login)
    form = robo_browser.get_form()
    form['kennung'] = username
    form['passwort'] = password
    robo_browser.submit_form(form)

    if not did_login_work(robo_browser):
        print("Your email or password was incorrect. Please try again.")
        print("")


def did_login_work(robo_browser):
    """Returns true if function does not find any input possibility"""
    for i in robo_browser.find_all("input", type="text"):
        if i.get("name") == "kennung":
            return False
    return True


def grab_odds(robo_browser, bet_urls):
    if isinstance(bet_urls, str):
        bet_urls = [bet_urls]
    for url in bet_urls:
        print("Grabbing ods for " + url)
        odds = []
        matchup = []
        gameday = {}
        robo_browser.open(url)
        for i in robo_browser.find_all("td"):
            attributes = i.attrs
            if len(attributes) == 0:
                continue
            elif 'kicktipp-time' in attributes['class']:
                if len(matchup) > 0:
                    gameday[str(matchup)] = {'odds': odds, 'teams': matchup}
                    matchup = []
                    odds = []
                continue
            elif 'kicktipp-wettquote' in attributes['class']:
                # due to cancelations or postponements some games don't have odds but have a matchup and tipp field
                try:
                    quote = float(i.get_text())
                except ValueError:
                    print('Was this match canceled or postponed? ' + str(matchup))
                    quote = 2.5
                odds.append(quote)
            elif "kicktipp-tippabgabe" in attributes['class']:
                continue
            else:
                team = i.get_text()
                matchup.append(team)
        gameday[str(matchup)] = {'odds': odds, 'teams': matchup}
    return gameday


def calc_results(gameday):
    """By considering odds, calculates match results"""
    print("Calculating Results")
    results = []

    for key in gameday:
        game_odds = gameday[key]['odds']
        diff = math.fabs(game_odds[0] - game_odds[2])
        if diff < 1.0:
            results.append(deuce)
        elif diff > 8.0:
            if game_odds[0] > game_odds[2]:
                results.append(team2_greatwin)
            else:
                results.append(team1_greatwin)
        else:
            if game_odds[0] > game_odds[2]:
                results.append(team2_win)
            else:
                results.append(team1_win)
    return results


def get_keys(robo_browser, url):
    print("Getting input keys for " + url)
    formkeys = []
    robo_browser.open(url)

    for i in robo_browser.find_all("input", inputmode="numeric"):
        formkeys.append(i.get("name"))
    formkeys = [formkeys[i:i + 2] for i in range(0, len(formkeys), 2)]
    return formkeys


def pass_results(robo_browser, bet_urls, results):
    for idx, url in enumerate(bet_urls):
        print("Passing Results to " + url)
        formkeys = get_keys(robo_browser, url)
        robo_browser.open(url)

        if len(formkeys) != len(results):
            raise ValueError

        form = robo_browser.get_form()
        for i in range(0, len(formkeys)):
            form[formkeys[i][0]].value = str(int(results[i][0]))
            form[formkeys[i][1]].value = str(int(results[i][1]))
        robo_browser.submit_form(form)


def grab_kicktipp_groups(robo_browser):
    group_names = []
    for i in robo_browser.find_all("a"):
        link = i.get("href").split("?")[0]
        name = i.contents
        link = link.replace("/", "")
        if len(link) == 0:
            continue
        if link in name[0]:
            group_names.append(link)
    return list(set(group_names))


def set_bet_urls(links):
    bet_urls = []
    for l in links:
        bet_urls.append("https://www.kicktipp.de/" + l + "/tippabgabe")
    return bet_urls


if __name__ == '__main__':
    browser = RoboBrowser(parser="html.parser", history=True)
    login(browser)
    betting_url = set_bet_urls(grab_kicktipp_groups(browser))
    my_odds = grab_odds(browser, betting_url)
    my_results = calc_results(my_odds)
    pass_results(browser, betting_url, my_results)
    print("Done!")
