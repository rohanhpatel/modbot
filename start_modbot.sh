#!/bin/bash

source /home/rhpatel/bot_env/bin/activate; nohup python3 -u modbot.py > watch_modbot.log 2>&1 < /dev/null & 
