#!/usr/bin/env python3
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

import os, string, subprocess, sys, time, random
#import subprocess

from flask import Flask, flash, redirect, render_template, \
     request, url_for
from flask_babel import gettext, ngettext
from flask_babel import Babel
from flask_babel import force_locale as babel_force_locale
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

debug=1

run_directory="/home/pi/proxmark3-web/"
proxmark3_rdv4_dir='../proxmark3'
proxmark3_rdv4_client=proxmark3_rdv4_dir + '/client/proxmark3'
logfile = "../card-reads.log"
db_file="/home/pi/proxmark3.db"

# Setup a dictionary for the serial port types
serial_port_list = { '/dev/tty.usbmodemiceman1', '/dev/ttyACM0' }

def get_card_data(data):
    #print(data)
    for line in data.split("\n"):
        if("TAG ID:" in line):
            print(str(line.strip()))
            if debug: line.split()
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

def log_card_data(card_data):
    if debug: 
        print("Writing date to the database...") 
        print(card_data)
    addCard = card_tbl(card_raw=card_data['raw_cardnumber'], card_number = card_data['card_number'], card_format = card_data['format_len'], card_oem = card_data['oem'], card_facility_code = card_data['facility_code'])
    db.session.add(addCard)
    db.session.commit()

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

if not exists(run_directory + "messages.pot"):
    subprocess.run(['pybabel', 'extract', '-F', run_directory + 'babel.cfg', '-o', 'messages.pot', '.'])
    subprocess.run(['pybabel', 'compile', '-d', run_directory + 'translations'])

if(True):

    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_pyfile('/home/pi/proxmark3-web/mysettings.cfg')
    babel = Babel(app)
    babel.init_app(app)
    #Set up the Database for storing cards
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////' + db_file
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db = SQLAlchemy(app)

    @babel.localeselector
    def get_locale():
        return request.accept_languages.best_match(['ko','zh','ja', 'ja_JP', 'en'])


    # Database Classes
    class card_tbl(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        time_stamp = db.Column(db.DateTime, nullable=False,
        default=datetime.utcnow)
        card_raw = db.Column(db.String(128))
        card_number = db.Column(db.String(128))
        card_format = db.Column(db.String(128))
        card_oem = db.Column(db.String(128))
        card_facility_code = db.Column(db.String(128))

        def __repr__(self):
            return '<card_raw {}>'.format(self.card_raw)

    app.config.from_mapping(
        SECRET_KEY=str(random.getrandbits(64))
    )

    if not os.path.exists(db_file):
        db.create_all()

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
                log_card_data(card)
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
                flash(gettext('ERROR: Could not read a card... please try again....'))
                return redirect(url_for('index'))

    @app.route('/hid/sim')
    def sim_hid_card():
        raw_cardnumber = request.args.get('raw_cardnumber')
        if debug:
            print('Got card raw: ' + str(raw_cardnumber))

        #Send hid simulate tag to proxmark3
        #write_hid = subprocess.run([proxmark3_rdv4_client, serial_port, '-c', 'lf hid sim ' + raw_cardnumber, '&' ], capture_output=True)
        write_hid = subprocess.Popen([proxmark3_rdv4_client, serial_port, '-c', 'lf hid sim ' + raw_cardnumber ])

        flash(gettext('Simulate Mode has been entered, please press the button on the PM3 to exit...'))
        return redirect(url_for('index'))

        #if('Simulating HID tag with ID' in write_hid.stdout.decode('ASCII')):
        #    flash('Simulating HID Tag with the PM3... Push the hardware button to cancel...')
        #    return redirect(url_for('index'))
        #if('ERROR: serial port' in write_hid.stdout.decode('ASCII')):
        #    flash('Serial port error')
        #    return render_template('card_list')

    @app.route('/write')
    def write_hid():
        raw_cardnumber = request.args.get('raw_cardnumber')
        if debug:
            print('Got card raw: ' + str(raw_cardnumber))

        # Write the raw card number to the card. Next is to take FC and CN input too.
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
                flash(gettext('ERROR: CARD DID NOT PROGRAM... TRY AGIAN.'))
                return redirect(url_for('index'))

    @app.route('/card/list')
    def card_list():
        card = card_tbl.query.all()
        #for line in card:
        #    print(line['card_number'])

        return render_template('cards.html', card = card)

    @app.route('/shutdown')
    def shutdown_os_now():
        subprocess.run(['sudo', '/sbin/shutdown', '-P']) 
        flash(gettext('System shutdown in progress....'))
        return redirect(url_for('index'))

        return render_template('cards.html', card = card)

    @app.route('/card/<card_id>')
    def card_mod(card_id):
        delCard = card_tbl.query.filter_by(id=card_id).first()
        db.session.delete(delCard)
        db.session.commit()

        if debug: print('Deleted card id: '+ str(card_id))
        flash(gettext('Card ') +card_id+ gettext(' was deleted from the database...'))
        return redirect(url_for('card_list'))

    @app.route('/wipe_card')
    def wipe_card():
        wipe_card = subprocess.run([proxmark3_rdv4_client, serial_port, '-c', 'lf t55xx wipe' ], capture_output=True)
        if('ERROR: serial port' in wipe_card.stdout.decode('ASCII')):
            flash('Serial port error')
            return redirect(url_for('index'))

        if(wipe_card.returncode == 0):
            flash(gettext('t5577 card wipe complete'))
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
                flash(gettext('Wrote default ID to card.'))
                return redirect(url_for('index'))
            else:
                flash(gettext('ERROR: CARD DID NOT PROGRAM... TRY AGIAN.'))
                return redirect(url_for('index'))



    @app.route('/')
    def index():
        return render_template('main.html')

#    return app

