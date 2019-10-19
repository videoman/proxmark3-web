#!/bin/bash

# this will install the flask service to autostart the web interface.

sudo cp proxmark3-web.py /etc/systemd/system/  && sudo systemctl daemon-reload && sudo systemctl enable proxmark3-web && sudo systemctl start proxmark3-web
