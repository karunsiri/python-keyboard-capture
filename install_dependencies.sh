set -e

sudo cp ./org.karunsiri.btkeyboard.conf /etc/dbus-1/system.d
sudo apt-get install -y \
  build-essential \
  pi-bluetooth \
  bluez \
  bluez-firmware \
  bluez-tools \
  libdbus-1-dev \
  libglib2.0-dev \
  libbluetooth-dev \
  libcairo2-dev \
  libgirepository1.0-dev
sudo usermod -G bluetooth -a pi
pip install evdev dbus-python pybluez pygobject
