"""
The KickTippTipper logs into your KickTipp account and automatically
submits its generated bets. The bets get calculated by considering
each teams odds.
"""
import robobrowser
from bs4 import BeautifulSoup
import math

url_login = "https://www.kicktipp.de/info/profil/login"
url_login_mobile = "https://m.kicktipp.de/info/profil/login"

#Possible Results, modify at will
deuce = [1,1]
team1_win = [2,1]
team2_win = [1,2]
team1_greatwin = [3,1]
team2_greatwin = [1,3]


def login():
    """Logs into useraccount"""
    print("Logging in")
    while True:
        username = input("Username: ")
        password = input("Password: ")
        for l in [url_login, url_login_mobile]:
            browser.open(l)
            form = browser.get_form()
            form['kennung'] = username
            form['passwort'] = password
            browser.submit_form(form)

        if not did_login_work():
            print("Your email or password was incorrect. Please try again.")
            print("")
        else:
            break
        
                
def did_login_work():
    """Returns true if function does not find any input possibility"""
    for i in browser.find_all("input",type="text"):
        if i.get("name") == "kennung":
            return False
    return True
        
def grab_odds():
    """Grabs latest odds for each match"""
    ret = []
    for url in url_betting:
        print("Grabbing ods for "+url)
        odds = []
        browser.open(url)
    
        for i in browser.find_all("td", class_="kicktipp-wettquote"):
            quote = float(i.get_text())
            odds.append(quote)
        odds = [odds[i:i+3] for i in range(0, len(odds), 3)]
        ret.append(odds)
    return ret


def calc_results(odds):
    """By considering odds, calculates match results"""
    print("Calculating Results")
    results = []
    
    for site in odds:
        sresults = []
        for i in site:
            diff = math.fabs(i[0]-i[2])
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
    for url in url_betting_mobile:
        print("Getting input keys for "+url)
        formkeys = []
        browser.open(url)
    
        for i in browser.find_all("input",type="tel"):
            formkeys.append(i.get("name"))
        formkeys = [formkeys[i:i+2] for i in range(0, len(formkeys), 2)]
        ret.append(formkeys)
    return ret


def pass_results(results):
    """Submit calculated results and save them"""
    for idx, url in enumerate(url_betting_mobile):
        print("Passing Results to "+url)
        formkeys = get_keys()
        browser.open(url)
        form = browser.get_form()

        #If some matches already have been played the results list needs to be adjusted
        if len(formkeys) != len(results):
            to_delete = len(results[idx])-len(formkeys)
            results[idx] = results[idx][to_delete:]

        for i in range(0,len(formkeys)):
            form[formkeys[idx][i][0]] = results[idx][i][0]
            form[formkeys[idx][i][1]] = results[idx][i][1]
        browser.submit_form(form)


def grab_beturl():
    """Searches for the bet-urls"""
    ret = []
    for i in browser.find_all("a"):
        link = i.get("href").split("?")[0]
        name = i.contents
        link = link.replace("/","")
        if link in name :
            ret.append(link)
    return ret

def set_bet_urls(links):
    """Sets bet-urls"""
    global url_betting
    global url_betting_mobile
    url_betting = []
    url_betting_mobile = []
    for l in links:
        url_betting.append("https://www.kicktipp.de/" + l + "/tippabgabe")
        url_betting_mobile.append("https://m.kicktipp.de/" + l + "/tippabgabe")
    
    
if __name__ == '__main__':
    browser = robobrowser.RoboBrowser(parser="html.parser", history=True)
    login()
    set_bet_urls(grab_beturl())
    my_odds = grab_odds()
    my_results = calc_results(my_odds)
    pass_results(my_results)
    print("Done!")
