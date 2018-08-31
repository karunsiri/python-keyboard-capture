# Terminate on error
set -e

sudo hciconfig hci0 down
sudo btmgmt discov yes
sudo btmgmt pairable on
sudo btmgmt connectable on
sudo btmgmt bondable on
sudo btmgmt name "Karun Keyboard"
sudo btmgmt class 5 64
sudo btmgmt power on
sudo hciconfig hci0 up
