#!/bin/bash
source /home/bot_manager/code/Discord-Ticker-Bots/.venv/bin/activate &
gunicorn -b 0.0.0.0:8000 -w 1 src.python.server:app --chdir /home/bot_manager/code/Discord-Ticker-Bots/src/python