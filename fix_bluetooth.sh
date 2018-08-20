# Terminate on error
set -e

sudo hciconfig hci0 down

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

sudo bluetoothctl <<EOF
discoverable on
pairable on
power on
agent KeyboardOnly
EOF

sudo hciconfig hci0 up
sudo hciconfig hci0 class 0x002540
