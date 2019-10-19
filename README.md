# proxmark3-web
Python Flask Web Interface for proxmark3 RDV4 hardware.

# Installation Instructions
These instructions assume you have Raspbian on your Pi already setup, and ready to go. [Raspbian Install] (https://www.raspberrypi.org/documentation/installation/installing-images/)
Once you have the card writen, you should enable SSH, per the instructons on [here] (https://linuxize.com/post/how-to-enable-ssh-on-raspberry-pi/)

SSH into your pi, and follow along.

## Install
### Proxymark3-rdv4 client
Download and install the proxmark3 client from the [RFID Research Group](https://github.com/RfidResearchGroup/proxmark3)

Further (and maybe more complete/updated) instructions for your OS cane be found [here](https://github.com/RfidResearchGroup/proxmark3/blob/master/doc/md/Installation_Instructions/Linux-Installation-Instructions.md)

#### update your apt cache for Raspbian
```shell
sudo apt-get update
```
#### Install the requirements
Note: this also will install python-flask, and does not include the qt5 GUI for proxmark. It's not needed.
```
sudo apt-get install --no-install-recommends git ca-certificates build-essential pkg-config \
libreadline-dev gcc-arm-none-eabi libnewlib-dev python-flask
```
#### Proxmark3-rdv4 code
Grab the code repo for proxmark3-rdv4
```shell
git clone https://github.com/RfidResearchGroup/proxmark3.git
```

#### Access right for the serial port
The 'pi' user should already be part of the 'dialout' groups. You can run the command `groups` to check if the user is in the dialout group first. If they are not, then you can run the following command from the proxmark3 directory.
```shell
make accessrights
```

#### Compile proxmark3
The main install instructions can be found in the git repo [here](https://github.com/RfidResearchGroup/proxmark3/blob/master/doc/md/Use_of_Proxmark/0_Compilation-Instructions.md)
Provided here for ease of use.

First things first- pull down the latest commits- and then compile as follows:
```shell
cd proxmark3
git pull
make clean && make all
sudo make install
```

Next test that you can access the proxmark3, and that you have access to the hardware via the serial port.
```shell
proxmark3 /dev/ttyACM0
```
Run a few  tests to see if you can access the proxmark4-rdv4 eg: `lf search` or `hf search`

#### Install proxmark-web
```shell
cd proxmark3-web
./install.sh
```
This will setup systemd to start the Flask Web interface on boot for you.

####

# proxmark-rdv-web
Python Flask Web Front End for Proxmark3 RDV unit.

To install the modules for this program, you shuld be able to do:
pip3 install flask


Then run the web app:
export FLASK_APP=proxmark-web.py
export FLASK_ENV=development
flask run
