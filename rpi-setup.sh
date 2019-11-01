#!/bin/bash
sudo systemctl stop dnsmasq && \
sudo systemctl stop hostapd && \
sudo cp /etc/dhcpcd.conf /tmp/dhcpcd.conf
cat <<EOF >>/tmp/dhcpcd.conf
interface wlan0
    static ip_address=192.168.4.1/24
    nohook wpa_supplicant
EOF
sudo cp /tmp/dhcpcd.conf /etc/dhcpcd.conf
sudo service dhcpcd restart

sudo mv /etc/dnsmasq.conf /etc/dnsmasq.conf.orig
cat <<EOF >/tmp/dnsmasq.conf
interface=wlan0      # Use the require wireless interface - usually wlan0
dhcp-range=192.168.4.2,192.168.4.20,255.255.255.0,24h

interface=br0
expand-hosts
domain=proxmark3-web.com
dhcp-range=192.168.20.100,192.168.20.150,12h
EOF
sudo mv /tmp/dnsmasq.conf /etc/dnsmasq.conf
sudo systemctl reload dnsmasq
echo -n "What do you want your Wifi Password to be?:[wifi-password] "
read wifipwd
if [ $wifipwd = '']
then
        wireless_password = "wifi-password"
else
        wireless_password = $wifipwd
fi
cat <<EOF >> /tmp/hostapd.conf
interface=wlan0
driver=nl80211
ssid=Proxmark3-web
hw_mode=g
channel=11
wmm_enabled=0
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=2
wpa_key_mgmt=WPA-PSK
wpa_pairwise=TKIP
rsn_pairwise=CCMP
EOF
echo -n "wpa_passphrase=$wifipwd" >> /tmp/hostapd.conf
sudo mv /tmp/hostapd.conf /etc/hostapd/hostapd.conf
sudo systemctl unmask hostapd
sudo systemctl enable hostapd
sudo systemctl start hostapd
