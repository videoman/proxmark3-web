#!/usr/bin/env python3
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

import os, string, subprocess, sys, time
#import subprocess

from flask import Flask, flash, redirect, render_template, \
     request, url_for

from datetime import datetime

debug=1
proxmark3_rdv4_dir='/home/pi/proxmark3'
proxmark3_rdv4_client=proxmark3_rdv4_dir + '/client/proxmark3'
logfile = "/home/pi/card-reads.log"
# Setup a dictionary for the serial port types
serial_port_list = { '/dev/tty.usbmodemiceman1', '/dev/ttyACM0' }

def get_card_data(data):
    #print(data)
    for line in data.split("\n"):
        if("TAG ID:" in line):
            print(str(line.strip()))
            line.split()
            cardsplit = line.split()
            card_data = {}
            card_data['raw_cardnumber'] = str(cardsplit[5])
            card_number = str(cardsplit[6])
            card_data['card_number'] = card_number.strip('()')
            card_data['format_len'] = str(cardsplit[10])
            card_data['oem'] = str(cardsplit[13])
            card_data['facility_code'] = str(cardsplit[16])
            #print('Raw: '+ raw_cardnumber +' Card Number: '+ card_number +' Card format: '+ format_len +' Facility: '+ facility_code )
            return(card_data)

def exists(path):
    """Test whether a path exists.  Returns False for broken symbolic links"""
    try:
        os.stat(path)
    except OSError:
        return False
    return True

serial_port = 0
while not serial_port:
    print("Looking for the serial port to use...")
    for device in set(serial_port_list):
        if(exists(device)):
            serial_port=device
            print("Setting serial port to: " + serial_port)
    if not serial_port:
        delay=10
        print("Serial device not found.... sleeping "+ str(delay) +" seconds - connect your Proxmark3-rdv4...")
        time.sleep(delay)

if(True):
    app = Flask(__name__, instance_relative_config=True)

    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='abc123',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

#    if test_config is None:
#        # load the instance config, if it exists, when not testing
#        app.config.from_pyfile('config.py', silent=True)
#    else:
        # load the test config if passed in
#        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    # a simple page that says hello
    @app.route('/hello')
    def hello():
        return 'Hello, World!'

    @app.route('/read/lf')
    def read_lf_card():
        cardnumber = subprocess.run([proxmark3_rdv4_client, serial_port, '-c', 'lf search'], capture_output=True)
        if('ERROR: serial port' in cardnumber.stdout.decode('ASCII')):
            flash('Serial port error')
            return redirect(url_for('index'))

        if(cardnumber.returncode == 0):
            if('Valid' in cardnumber.stdout.decode('ASCII')):
                card_read=1
                #return 'Hello, World!\n<br>Raw Card Number:' + raw_cardnumber + '<br> Card ID:' + card_number + ' FC:' + facility_code
                card = get_card_data(cardnumber.stdout.decode('ASCII'))
                if debug: print(card)
                current_time = datetime.now().isoformat(timespec='seconds')
                print(str(current_time) + ' _Card Used_ ' + card, file=open(logfile, "a"))
                return render_template('main.html', 
                        card_number=card['card_number'], 
                        oem=card['oem'], 
                        facility_code=card['facility_code'], 
                        raw_cardnumber=card['raw_cardnumber'], 
                        card_read=card_read
                        )

    @app.route('/read/hid')
    def read_hid_card():
        cardnumber = subprocess.run([proxmark3_rdv4_client, serial_port, '-c', 'lf hid read'], capture_output=True)
        if('ERROR: serial port' in cardnumber.stdout.decode('ASCII')):
            flash('Serial port error')
            return redirect(url_for('index'))

        if(cardnumber.returncode == 0):
            if('HID Prox TAG ID:' in cardnumber.stdout.decode('ASCII')):
                card = get_card_data(cardnumber.stdout.decode('ASCII'))
                if(debug): print("Card number:" + str(card))
                current_time=str(datetime.now().isoformat(timespec='seconds'))
                print(current_time + ' _Card Used_ ' + str(card), file=open(logfile, "a"))
                card_read=1
                #return 'Hello, World!\n<br>Raw Card Number:' + raw_cardnumber + '<br> Card ID:' + card_number + ' FC:' + facility_code
                return render_template('main.html', 
                        card_number=card['card_number'], 
                        oem=card['oem'], 
                        facility_code=card['facility_code'], 
                        raw_cardnumber=card['raw_cardnumber'], 
                        card_read=card_read 
                        )
            else:
                flash('ERROR: Could not read a card... please try again....')
                return redirect(url_for('index'))

    @app.route('/write')
    def write_hid():
        raw_cardnumber = request.args.get('raw_cardnumber')
        print('Got card raw: ' + str(raw_cardnumber))

        write_hid = subprocess.run([proxmark3_rdv4_client, serial_port, '-c', 'lf t55xx wipe ; lf hid clone ' + raw_cardnumber + ' ; lf hid read' ], capture_output=True)
        if('ERROR: serial port' in write_hid.stdout.decode('ASCII')):
            flash('Serial port error')
            return redirect(url_for('index'))

        if(write_hid.returncode == 0):
            #print(write_hid.stdout.decode('ASCII'))
            if('HID Prox TAG ID: ' + raw_cardnumber.lower() in write_hid.stdout.decode('ASCII')):
                flash('Wrote ID to card.')
                return redirect(url_for('index'))
            else:
                flash('ERROR: CARD DID NOT PROGRAM... TRY AGIAN.')
                return redirect(url_for('index'))


    @app.route('/wipe_card')
    def wipe_card():
        wipe_card = subprocess.run([proxmark3_rdv4_client, serial_port, '-c', 'lf t55xx wipe' ], capture_output=True)
        if('ERROR: serial port' in wipe_card.stdout.decode('ASCII')):
            flash('Serial port error')
            return redirect(url_for('index'))

        if(wipe_card.returncode == 0):
            flash('t5577 card wipe complete')
            return redirect(url_for('index'))

    @app.route('/provision_card')
    def make_new_card():
        # This writes a FC of 127, and a card ID of 31337 to the t5577 cards
        #new_hid_id = subprocess.run([proxmark3_rdv4_client, serial_port, '-c', 'lf t55xx wipe ; lf hid clone 2004FEF4D3 ; lf hid read' ], capture_output=True)
        new_hid_id = subprocess.run([proxmark3_rdv4_client, serial_port, '-c', 'lf hid clone 1029a0f4d2 ; lf hid read' ], capture_output=True)
        if('ERROR: serial port' in new_hid_id.stdout.decode('ASCII')):
            flash('Serial port error')
            return redirect(url_for('index'))

        if(new_hid_id.returncode == 0):
            if('HID Prox TAG ID: 1029a0f4d2' in new_hid_id.stdout.decode('ASCII')):
                flash('Wrote default ID to card.')
                return redirect(url_for('index'))
            else:
                flash('ERROR: CARD DID NOT PROGRAM... TRY AGIAN.')
                return redirect(url_for('index'))

    @app.route('/')
    def index():
        return render_template('main.html')

#    return app

