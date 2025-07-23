# GGST Discord Bot

This bot posts Guilty Gear Strive match results to a Discord channel using the Puddle Farm API.

## Setup

1. Install the dependencies:

```bash
pip install -r requirements.txt
```

2. Edit `config.py` and set your Discord bot token.
3. Run the bot:

```bash
python bot.py
```

The bot checks new matches every five minutes and announces them in the channel specified in `config.py`.
