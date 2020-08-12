# RX and TX in Raspi0

This python code implements a RX and Tx for the RF24 module.

The code implements two diiferent transmision types:

- **Single point to point communication:** It transmites a compressed file from rx to tx using a basic stop&wait with the builtin ACK

- **Network comunication:** Several nodes try to collaborate to transmit the file, the nodes do a network discovery. You can check the protocol specification on the [pdf](./NetworkProtocolSpec.pdf).

## Dependency installation

```bash
#Install some dependency libraries
sudo apt-get install python2.7 python2.7-dev \
                     libpython2.7 libpython2.7-dev \
                     automake libboost-python-dev \
                     python-setuptools

#Install the transitions library
sudo pip install transitions

#Steps for the antenna module
unzip bcm2835-1.60.zip
cd bcm2835-1.60/
chmod +x configure
sudo ./configure
sudo make
sudo make check
sudo make install
sudo make check

cd ..
unzip RF24-master.zip
cd RF24-master/
sudo ./configure --driver=SPIDEV
sudo make install -B

# Configure swap file to 1000 MB for building
sudo nano /etc/dphys-swapfile
# Change the line from ‘CONF_SWAPSIZE=100’ to CONF_SWAPSIZE=1000‘

# Reboot raspberry
sudo shutdown -r now

cd RF24-master/pyRF24/
sudo chmod +x setup.py
sudo python setup.py build #takes time
sudo python setup.py install

```
