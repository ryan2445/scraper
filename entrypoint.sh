#!/bin/bash
set -e

Xvfb :99 -screen 0 1366x768x24 &

export DISPLAY=:99

python -u main.py
