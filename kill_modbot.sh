#!/bin/bash

ps -eo pid,command | grep modbot | grep -v grep | awk '{print $1}' | xargs -r kill -9
