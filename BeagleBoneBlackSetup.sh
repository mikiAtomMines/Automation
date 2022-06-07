# Sebastian Miki-Silva
# June 7th, 2022

echo 'Updating sudo...'
yes | sudo apt-get update
yes | sudo apt-get upgrade
printf '\n'


echo 'Installing zip and unzip...'
yes | sudo apt install zip
yes | sudo apt install unzip
printf '\n'


echo 'Intalling git...'
yes | sudo apt-get install git git-core
printf '\n'


echo 'Installing Python3 libraries...'
yes | pip3 install simple_pid
yes | pip3 install pyserial
yes | sudo apt-get install python3-matplotlib
printf '\n'


echo 'Installing MCC Universal Library for Linux...'
yes | sudo apt-get install gcc g++ make
yes | sudo apt-get install libusb-1.0-0-dev
yes | wget -N https://github.com/mccdaq/uldaq/releases/download/v1.2.1/libuldaq-1.2.1.tar.bz2
yes | tar -xvjf libuldaq-1.2.1.tar.bz2
cd libuldaq-1.2.1
yes | ./configure && make
yes | sudo make install
yes | pip3 install uldaq