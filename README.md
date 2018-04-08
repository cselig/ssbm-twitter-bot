# SSBM Stats Twitter Bot

This bot operates of a small dataset pulled from the Tafostats data. It can answer questions such
as the following:

- Marth vs Fox on Pokemon Stadium
- Falcon vs Sheik
- What's Falco's best counterpick vs puff?

This bot isn't currently running 24/7 as the subset of data it operates on is quite small, and
I don't want it get too much usage without first backing it up with a bigger and more comprehensive
dataset. When the bot is running, you can tweet @ssbm_stats_bot.
If you've got a different solution to getting more matchup data other than scraping
Tafostats, hit me up!

## Setup

- Install python 3.6
- Run `pip install -r requirements.txt`
- Put your Twitter API access keys at `local/keys.txt`.
- Put the sqlite3 database at `data/ssbm.db`. Ensure that it has the schema defined in
`schema.txt`. The database that @ssbm_stats_bot uses is not publicly available at the time.
- In `listener.py`, change the username for mentions to whatever account you are running this bot from.

## Running
To run the bot, do `python listener.py`.
