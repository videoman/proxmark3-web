#!/bin/bash

# this will install the flask service to autostart the web interface.

sudo cp proxmark3-web.py /etc/systemd/system/  && systemctl daemon-reload && systemctl enable proxmark3-web && systemctl start proxmark3-web
