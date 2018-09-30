# electrum-personal-server-GUI
gui in python-tk and shell script for Belcher's Electrum Personal Server


Dependencies are the following:


wget python3-tk pyqt5-dev-tools git python3-setuptools python3-pip tor


It downloads bitcoind, electrum, and electrum personal server. It runs bitcoind and syncs the chain, with a progress indicator. It modifies electrum to have menu items to add the MPKs and addresses to the EPS config file. When it broadcasts, it opens another instance of electrum over tor and broadcasts, then closes that instance. It has status indicator for bitcoind and electrum-personal-server

https://github.com/robust-cuttlefish/electrum-personal-server-GUI/blob/master/Screenshot_2018-09-27.jpg
