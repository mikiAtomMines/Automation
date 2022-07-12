#!/bin/bash

# Sebastian Miki-Silva
# June 7th, 2022

cd ~/
echo 'Updating sudo...'
sudo apt-get update
sudo apt-get upgrade
printf '\n'


echo 'Installing zip and unzip...'
sudo -S apt install zip
printf '\n'


echo 'Intalling git...'
sudo apt-get install git git-core
printf '\n'


echo 'Installing Python3 libraries...'
pip3 install simple_pid
pip3 install pyserial
sudo apt-get -y install pyvisa
sudo apt-get install python3-matplotlib
printf '\n'

echo 'Installing MCC Universal Library for Linux...'
sudo apt-get install gcc g++ make
sudo apt-get install libusb-1.0-0-dev
wget -N https://github.com/mccdaq/uldaq/releases/download/v1.2.1/libuldaq-1.2.1.tar.bz2
tar -xvjf libuldaq-1.2.1.tar.bz2
cd libuldaq-1.2.1
./configure && make
sudo -S make install
pip3 install uldaq
cd ~/
printf '\n'

echo 'Downloading Automation library...'
git clone https://github.com/mikiAtomMines/Automation.git
printf '\n'

cd /
echo 'Finished'
printf '\n'
