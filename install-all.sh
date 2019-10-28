#!/bin/bash

# this script will install proxmark3-rdv4, and all the things.

sudo apt-get update && sudo apt-get -y install --no-install-recommends git ca-certificates build-essential pkg-config \
libreadline-dev gcc-arm-none-eabi libnewlib-dev python3-flask python3-flask-sqlalchemy hostapd python3-pip python3-dateutil python3-dateparser libev-dev gunicorn3 && \
sudo pip3 install --upgrade pip && \
sudo pip3 install datetime && \
sudo pip3 install Flask-Babel && \
cd ~ && git clone https://github.com/RfidResearchGroup/proxmark3.git &&\
cd ~/proxmark3/ && git pull && make clean && make all && sudo make install &&\
cd ~/proxmark3-web && \
./install.sh

