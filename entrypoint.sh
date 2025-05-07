#!/bin/bash
set -e

Xvfb :99 -screen 0 1366x768x24 &
export DISPLAY=:99

export HTTP_PROXY="http://$PROXY_HOST"
export http_proxy="http://$PROXY_HOST"
export HTTPS_PROXY="https://$PROXY_HOST"
export https_proxy="https://$PROXY_HOST"
export NO_PROXY="localhost,127.0.0.1"
export no_proxy="localhost,127.0.0.1"

python -u main.py
