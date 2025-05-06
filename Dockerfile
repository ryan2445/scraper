FROM python:3.13-slim

RUN apt-get update && apt-get install -y \
    wget \
    xvfb

RUN wget -q -O ./google-chrome.deb https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb && \
    apt-get install -y ./google-chrome.deb && \
    rm ./google-chrome.deb

COPY ./python .
RUN pip install -r requirements.txt

COPY ./entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
