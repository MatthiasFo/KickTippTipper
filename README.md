# KickTippTipper
KickTippTipper is an **automatic better** for the website [http://www.kicktipp.com](http://www.kicktipp.com). 
Its goal is to **relieve the user** by undertaking the duty to bet on a weekly basis. 

You need to put your login credentials into ``credentials.json`` with the following data inside: ``{"username":  "your-login-name", "password":  "your-password"}``.
The ``tipper.py`` script automatically logs into your **KickTipp account** and submits bets. 
The bets get **calculated by considering each teams odds** with a heuristic.

You can easily replace the ``calc_results`` function with your own result estimation function and re-use the automated tipping functions.

## Result algorithm

The script uses the latest betting odds for each team of each match. To predict realistic results it subtracts the two numbers and calculates the absolute value. There are three possible results for a match:

* If the absolute value is less than 1 (both teams are equally good) the result will be **(1:1)**
* If the absolute value is bigger than 8 (one team is way stronger than the other) the result will be **(3:1)**
* If the absolute value is bigger than 1 but less than 8 (one team is a bit stronger than the other) the result will be **(2:1)**

All match results can optionally be changed.