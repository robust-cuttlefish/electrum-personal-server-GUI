#!/usr/bin/env python3
#
# Copyright (c) 2018 robust-cuttlefish
#
# Permission is hereby granted, free of charge, to any person obtaining a copy of
# this software and associated documentation files (the "Software"), to deal in
# the Software without restriction, including without limitation the rights to
# use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
# of the Software, and to permit persons to whom the Software is furnished to do
# so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY,
# WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
# CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#
#sudo apt install -y python3-tk tor pyqt5-dev-tools python3-pip python3-setuptools 
# recommended: git, qrencode, zbar-tools
#chmod +x eps-gui.py
#./eps-gui.py
from tkinter import *
import subprocess
import json
import secrets
import os
import fileinput
import re
import string
import time

root = Tk()
root.title('Electrum Personal Server GUI')

bitcoinsum="b'6ccc675ee91522eee5785457e922d8a155e4eb7d5524bd130eb0ef0f0c4a6008  bitcoin-0.17.0.1-x86_64-linux-gnu.tar.gz\\n'"
electrumsum="b'9ff70ac0a8cefe188b05ca0e2865dd1d32eda624080051af769784c04dccc2dc  3.2.3.tar.gz\\n'"
epssum="b'6c4f48068398df22e2326d8211a71f9d53a9ba28a40a5c555f519d5c84b61710  eps-v0.1.5.tar.gz\\n'"
seconds = 0
rpcpass = 0
rpcpass=secrets.randbelow(10**40)
checksumtrigger=0

def num(s):
    try:
        return int(s)
    except ValueError:
        return float(s)

def monitor_ibd():
    global seconds
    seconds += 1
    f = open('./bitcoind_status', 'w')
    f.write("ps aux | grep bitcoin-0.17.0")
    f.close()
    args = str("chmod +x bitcoind_status").split()
    popen = subprocess.Popen(args)
    popen.wait()
    args = str("bash ./bitcoind_status").split()
    popen = subprocess.Popen(args, stdout=subprocess.PIPE)
    popen.wait()
    output = popen.stdout.read()
    bitcoind_status="bitcoind is #not# running"
    last_line = ""
    if "datadir" in str(output):
        bitcoind_status="bitcoind *is* running"
        f = open('./rescan_status', 'w')
        f.write("tail ./.bitcoin/debug.log | grep rescanning | head -1")
        f.close()
        args = str("chmod +x rescan_status").split()
        popen = subprocess.Popen(args)
        popen.wait()
        args = str("bash ./rescan_status").split()
        popen = subprocess.Popen(args, stdout=subprocess.PIPE)
        popen.wait()
        output = popen.stdout.read()
        last_line=str(output)
        f.close()
        if last_line=="""b''""":
            last_line=""
        else:
            last_line="\n"+last_line[2:-2]

    f = open('./eps_status', 'w')
    f.write("ps aux | grep server.py")
    f.close()
    args = str("chmod +x eps_status").split()
    popen = subprocess.Popen(args)
    popen.wait()
    args = str("bash ./eps_status").split()
    popen = subprocess.Popen(args, stdout=subprocess.PIPE)
    popen.wait()
    output = popen.stdout.read()
    eps_status="eps is #not# running"
    if "python3 ./server.py" in str(output):
        eps_status="eps *is* running"

    args = str("./bitcoin-0.17.0/bin/bitcoin-cli -rpcpassword=" + str(rpcpass) + " -rpcuser=user getblockchaininfo").split()
    popen = subprocess.Popen(args, stdout=subprocess.PIPE)
    popen.wait()
    output = popen.stdout.read()
    bht="1"
    bhd="2"
    try:
        j = json.loads(output)
        bht=j['blocks']
        bhd=j['headers']
    except Exception:
        pass

    fbht = float(str(bht))
    fbhd = float(str(bhd))
    if fbhd == 0:
        fbhd = 1
    progressbar=int(10000*(fbht-0.0)/fbhd)-1
    fullbars=progressbar//1000
    fullbarsfiller=10-fullbars
    partbar=progressbar%1000//10
    partbarfiller=100-partbar
    progressbar_string=""
    if (fbhd-fbht)>144:
        progressbar_string += "\n"
        for x in range(1,fullbars):
            progressbar_string=progressbar_string + "0"*101+"\n"
        for x in range(0,partbar):
            progressbar_string=progressbar_string + "0"
        progressbar_string=progressbar_string + str(progressbar%10)
        for x in range(0,partbarfiller):
            progressbar_string=progressbar_string + "_"
        progressbar_string=progressbar_string + "\n"
        for x in range(1,fullbarsfiller):
            progressbar_string=progressbar_string + "_"*101+"\n"
    blocks['text'] = str(eps_status) + "\n" + str(bitcoind_status) + "\n blocks: " + str(bht) + "\n" + "headers: " + str(bhd) +  progressbar_string + last_line
    blocks.after(3333, monitor_ibd)

def stop_bitcoind():
    args = "pkill bitcoind".split()
    popen = subprocess.Popen(args)
    f = open('./stop_server', 'w')
    f.write("ps aux | grep \"python3 ./server.py\" | awk '{print $2}' | xargs kill\nsleep 3")
    f.close()
    args = "chmod +x ./stop_server".split()
    popen = subprocess.Popen(args)
    args = "bash ./stop_server".split()
    popen = subprocess.Popen(args)
    popen.wait()

def stop_eps():
    f = open('./stop_server', 'w')
    f.write("ps aux | grep \"python3 ./server.py\" | awk '{print $2}' | xargs kill\nsleep 3")
    f.close()
    args = "chmod +x ./stop_server".split()
    popen = subprocess.Popen(args)
    args = "bash ./stop_server".split()
    popen = subprocess.Popen(args)
    popen.wait()

def start_eps():
    stop_eps()

    if os.path.exists("./eps/config.cfg")==True:
        args = "rm ./eps/config.cfg".split()
        popen = subprocess.Popen(args)
        popen.wait()
        print ("file deleted")

    if os.path.exists("./eps.cfg")==True:
        f = open("./eps.cfg",'r')
        filedata = f.read()
        f.close()
        newdata = filedata.replace("rpc_password =",str("rpc_password = "+str(rpcpass)+"\n#"))
        f = open("./eps.cfg",'w')
        f.write(newdata)
        f.close()
        print ("password updated")

        args = "cp ./eps.cfg ./eps/config.cfg".split()
        popen = subprocess.Popen(args)
        popen.wait()

    if os.path.exists("./eps.cfg")==False:
        args = "cp ./eps/config.cfg_sample ./eps.cfg".split()
        popen = subprocess.Popen(args)
        popen.wait()

        f = open("./eps.cfg",'r')
        filedata = f.read()
        f.close()      
        newdata = filedata.replace("#rpc_user =","rpc_user = user")
        f = open("./eps.cfg",'w')
        f.write(newdata)
        f.close()

        f = open("./eps.cfg",'r')
        filedata = f.read()
        f.close()
        newdata = filedata.replace("#rpc_password =",str("rpc_password = "+str(rpcpass)))
        f = open("./eps.cfg",'w')
        f.write(newdata)
        f.close()
        print ("password")

        f = open("./eps.cfg",'r')
        filedata = f.read()
        f.close()
        newdata = filedata.replace("## Add electrum master public keys to this section\n## Create a wallet in electrum then go Wallet -> Information to get the mpk\n\n#any_name_works = xpub661MyMwAqRbcFseXCwRdRVkhVuzEiskg4QUp5XpUdNf2uGXvQmnD4zcofZ1MN6Fo8PjqQ5cemJQ39f7RTwDVVputHMFjPUn8VRp2pJQMgEF\n\n# Multisig wallets use format `required-signatures [list of master pub keys]`\n#multisig_wallet = 2 xpub661MyMwAqRbcFseXCwRdRVkhVuzEiskg4QUp5XpUdNf2uGXvQmnD4zcofZ1MN6Fo8PjqQ5cemJQ39f7RTwDVVputHMFjPUn8VRp2pJQMgEF xpub661MyMwAqRbcFseXCwRdRVkhVuzEiskg4QUp5XpUdNf2uGXvQmnD4zcofZ1MN6Fo8PjqQ5cemJQ39f7RTwDVVputHMFjPUn8VRp2pJQMgEF\n\n\n[watch-only-addresses]\n## Add addresses to this section\n\n#addr = 1DuqpoeTB9zLvVCXQG53VbMxvMkijk494n\n# A space separated list is accepted\n#my_test_addresses = 3Hh7QujVLqz11tiQsnUE5CSL16WEHBmiyR 1PXRLo1FQoZyF1Jhnz4qbG5x8Bo3pFpybz bc1qar0srrr7xfkvy5l643lydnw9re59gtzzwf5mdq\n",str("\n[watch-only-addresses]\n"))
        f = open("./eps.cfg",'w')
        f.write(newdata)
        f.close()

        f = open("./eps.cfg",'r')
        filedata = f.read()
        f.close()
        newdata = filedata.replace("datadir = ","datadir = ./")
        f = open("./eps.cfg",'w')
        f.write(newdata)
        f.close()

        args = "cp ./eps.cfg ./eps/config.cfg".split()
        popen = subprocess.Popen(args)
        popen.wait()

    f = open('./start_server', 'w')
    f.write("cd eps\n./server.py\n")
    f.close()
    args = str("chmod +x start_server").split()
    popen = subprocess.Popen(args)
    popen.wait()
    args = str("bash ./start_server").split()
    popen = subprocess.Popen(args)

def start_eps_rescan(bh):
    start_eps()
    args = str("./bitcoin-0.17.0/bin/bitcoin-cli -rpcpassword=" + str(rpcpass) + " -rpcuser=user rescanblockchain " + str(bh) ).split()
    popen = subprocess.Popen(args)
    #popen.wait()
    
def start_eps_rescan_1():
    start_eps_rescan(1)
def start_eps_rescan_227088():
    start_eps_rescan(227088)
def start_eps_rescan_272448():
    start_eps_rescan(272448)
def start_eps_rescan_323712():
    start_eps_rescan(323712)
def start_eps_rescan_354528():
    start_eps_rescan(354528)
def start_eps_rescan_376992():
    start_eps_rescan(376992)
def start_eps_rescan_396000():
    start_eps_rescan(396000)
def start_eps_rescan_414000():
    start_eps_rescan(414000)
def start_eps_rescan_429840():
    start_eps_rescan(429840)
def start_eps_rescan_444816():
    start_eps_rescan(444816)
def start_eps_rescan_461088():
    start_eps_rescan(461088)
def start_eps_rescan_476208():
    start_eps_rescan(476208)
def start_eps_rescan_496080():
    start_eps_rescan(496080)
def start_eps_rescan_542000():
    start_eps_rescan(530000)

def start_electrum():
    start_eps()
    if os.path.isdir("./.electrum")==False:
        args = "mkdir .electrum".split()
        popen = subprocess.Popen(args)
        popen.wait()
    args = "rm -f ./.electrum/recent_servers".split()
    popen = subprocess.Popen(args)
    popen.wait()

    f = open('./electrum-3.2.3/electrum/servers.json', 'w')
    f.write("{\n    \"127.0.0.1\": {\n        \"pruning\": \"-\",\n        \"s\": \"50002\",\n        \"version\": \"1.2\"\n    }\n}\n")
    f.close()
    os.chdir("./electrum-3.2.3")
    args = "./run_electrum --oneserver --server 127.0.0.1:50002:s -D ../.electrum".split()
    popen = subprocess.Popen(args)
    os.chdir("../")

    if os.path.isdir("./.electrum-broadcast")==False:
        args = "mkdir .electrum-broadcast".split()
        popen = subprocess.Popen(args)
        popen.wait()
    args = "rm -f ./.electrum-broadcast/recent_servers".split()
    popen = subprocess.Popen(args)
    popen.wait()

    #os.chdir("./electrum-3.2.3-broadcast")
    #args = "./run_electrum -p socks5:localhost:9050 -D ../.electrum-broadcast".split()
    #popen = subprocess.Popen(args)
    #os.chdir("../")

    #./run_electrum daemon start -p socks5:localhost:9050 -D ../.electrum-broadcast -s wsw6tua3xl24gsmi264zaep6seppjyrkyucpsmuxnjzyt3f3j6swshad.onion:50002:s

def start_bitcoind():
    if os.path.isdir("./.bitcoin")==False:
        args = "mkdir .bitcoin".split()
        popen = subprocess.Popen(args)
        popen.wait()
    f = open('./.bitcoin/bitcoin.conf', 'w')
    f.write("txindex=1\nrpcpassword="+str(rpcpass)+"\nrpcuser=user\nserver=1\nwalletbroadcast=0")
    f.close()
    args = "./bitcoin-0.17.0/bin/bitcoind -datadir=./.bitcoin -walletbroadcast=0".split()
    popen = subprocess.Popen(args)

def start_all():
    start_electrum()
    start_eps()
    start_bitcoind()

def verify_bitcoind():
    global checksumtrigger
    checksums = ""
    if checksumtrigger==1:
        return
    checksumfail=0

    if os.path.exists("./bitcoin-0.17.0.1-x86_64-linux-gnu.tar.gz")==False:
        args = "wget https://bitcoincore.org/bin/bitcoin-core-0.17.0.1/bitcoin-0.17.0.1-x86_64-linux-gnu.tar.gz".split()
        popen = subprocess.Popen(args)
        popen.wait()
    args = "rm -rf ./bitcoin-0.17.0".split()
    popen = subprocess.Popen(args)
    popen.wait()
    args = "sha256sum bitcoin-0.17.0.1-x86_64-linux-gnu.tar.gz".split()
    popen = subprocess.Popen(args, stdout=subprocess.PIPE)
    popen.wait()
    output = popen.stdout.read()
    f = open('./bitcoin-0.17.0.1-x86_64-linux-gnu.tar.gz.SHA256SUM', 'w')
    f.write(str(output))
    f.close()
    if str(output)==bitcoinsum:
        checksums = checksums + "bitcoin checksums match"
        args = "tar xf bitcoin-0.17.0.1-x86_64-linux-gnu.tar.gz".split()
        popen = subprocess.Popen(args)
        popen.wait()
    else:
        args = "rm bitcoin-0.17.0.1-x86_64-linux-gnu.tar.gz".split()
        popen = subprocess.Popen(args)
        popen.wait()
        checksumfail=1
        Button(root, fg='blue', text=str(output) + "\n" + bitcoinsum, font='monospace').pack()
 
    if os.path.exists("./3.2.3.tar.gz")==False:
        args = "wget https://github.com/spesmilo/electrum/archive/3.2.3.tar.gz".split()
        popen = subprocess.Popen(args)
        popen.wait()
    args = "rm -rf ./electrum-3.2.3".split()
    popen = subprocess.Popen(args)
    popen.wait()
    args = "sha256sum 3.2.3.tar.gz".split()
    popen = subprocess.Popen(args, stdout=subprocess.PIPE)
    popen.wait()
    output = popen.stdout.read()
    f = open('./3.2.3.tar.gz.sha256', 'w')
    f.write(str(output))
    f.close()
    if str(output)==electrumsum:
        if checksumtrigger==0:
            checksums = checksums + " - "
        checksums = checksums + "electrum checksums match"
        args = "tar xf 3.2.3.tar.gz".split()
        popen = subprocess.Popen(args)
        popen.wait()
        args = "rm -rf electrum-3.2.3-broadcast".split()
        popen = subprocess.Popen(args)
        popen.wait()
        args = "mv electrum-3.2.3 electrum-3.2.3-broadcast".split()
        popen = subprocess.Popen(args)
        popen.wait()
        args = "tar xf 3.2.3.tar.gz".split()
        popen = subprocess.Popen(args)
        popen.wait()
        f = open("./electrum-3.2.3/electrum/gui/qt/main_window.py",'r')
        filedata = f.read()
        f.close()
        newdata = filedata.replace("""
    def show_master_public_keys(self):
""","""
    def transfer_address_es_to_node(self):
        from .address_list import AddressList
        l = self.wallet.get_receiving_addresses() + self.wallet.get_change_addresses() 
        wallet_type = self.wallet.storage.get('wallet_type', '')

        import re
        addresses_string=(str(l)[2:-2])
        if "imported" in str(wallet_type):
            addresses_string=addresses_string.replace("', '"," ")
            address_strings=addresses_string.split(" ")
            xx=0
            for x in address_strings:
                f = open("../eps.cfg",'r')
                filedata = f.read()
                f.close()
                newdata = filedata
                if str(address_strings[xx]) not in str(filedata):
                    newdata = filedata.replace("[watch-only-addresses]\\n",str("[watch-only-addresses]\\n\\n" + str(address_strings[xx]) + " = " + str(address_strings[xx])+"\\n"))
                f = open("../eps.cfg",'w')
                f.write(newdata)
                f.close()
                xx+=1

        f = open("../eps.cfg",'r')
        filedata = f.read()
        f.close()
        
        filedata_a, filedata_b = filedata.split("[master-public-keys]")
        filedata_a, filedata_b = filedata_b.split("[bitcoin-rpc]")
        filedata_a="[master-public-keys]\\n"+filedata_a
        
        dialog = WindowModalDialog(self, _("Master Public Keys Were Transferred to Full Node"))
        dialog.setMinimumSize(1270, 100)
        mpk_list = self.wallet.get_master_public_keys()
        vbox = QVBoxLayout()
        wallet_type = self.wallet.storage.get('wallet_type', '')

        grid = QGridLayout()
        basename = os.path.basename(self.wallet.storage.path)
        grid.addWidget(QLabel(_("Wallet name")+ ':'), 0, 0)
        grid.addWidget(QLabel(basename), 0, 1)
        grid.addWidget(QLabel(_("Wallet type")+ ':'), 1, 0)
        grid.addWidget(QLabel(wallet_type), 1, 1)
        grid.addWidget(QLabel(_("Script type")+ ':'), 2, 0)
        grid.addWidget(QLabel(self.wallet.txin_type), 2, 1)
        grid.addWidget(QLabel(str(filedata_a)), 3, 0)
        vbox.addLayout(grid)
        vbox.addStretch(1)
        
        vbox.addLayout(Buttons(CloseButton(dialog)))
        dialog.setLayout(vbox)
        dialog.exec_()


    def transfer_public_keys_to_node(self):
        import re
        dialog = WindowModalDialog(self, _("Master Public Keys Were Transferred to Full Node"))
        dialog.setMinimumSize(1270, 100)
        mpk_list = self.wallet.get_master_public_keys()
        vbox = QVBoxLayout()
        wallet_type = self.wallet.storage.get('wallet_type', '')

        mpk_string=(str(mpk_list)[2:-2])
        if "of" not in str(wallet_type):
            mpk_num=0
        else:
            mpk_num=int(re.sub("of.*","",str(wallet_type)))
        if mpk_num>0:
            mpk_string=str(mpk_num)+" "+mpk_string.replace("', '"," ")
        else:
            mpk_string=mpk_string.replace("', '"," ")

        f = open("../eps.cfg",'r')
        filedata = f.read()
        f.close()
        newdata = filedata
        if str(mpk_string) not in str(filedata):
            newdata = filedata.replace("[master-public-keys]\\n",str("[master-public-keys]\\n" + str(mpk_string)[-11:] + " = " + str(mpk_string)+"\\n"))
        f = open("../eps.cfg",'w')
        f.write(newdata)
        f.close()
        f = open("../eps.cfg",'r')
        filedata = f.read()
        filedata_a, filedata_b = filedata.split("[master-public-keys]")
        filedata_a, filedata_b = filedata_b.split("[bitcoin-rpc]")
        filedata_a="[master-public-keys]\\n"+filedata_a

        grid = QGridLayout()
        basename = os.path.basename(self.wallet.storage.path)
        grid.addWidget(QLabel(_("Wallet name")+ ':'), 0, 0)
        grid.addWidget(QLabel(basename), 0, 1)
        grid.addWidget(QLabel(_("Wallet type")+ ':'), 1, 0)
        grid.addWidget(QLabel(wallet_type), 1, 1)
        grid.addWidget(QLabel(_("Script type")+ ':'), 2, 0)
        grid.addWidget(QLabel(self.wallet.txin_type), 2, 1)
        grid.addWidget(QLabel(str(filedata_a)), 3, 0)
        vbox.addLayout(grid)
        if self.wallet.is_deterministic():
            mpk_text = ShowQRTextEdit()
            mpk_text.setMaximumHeight(150)
            mpk_text.addCopyButton(self.app)
            def show_mpk(index):
                mpk_text.setText(mpk_list[index])
            # only show the combobox in case multiple accounts are available
            if len(mpk_list) > 1:
                def label(key):
                    if isinstance(self.wallet, Multisig_Wallet):
                        return _("cosigner") + ' ' + str(key+1)
                    return ''
                labels = [label(i) for i in range(len(mpk_list))]
                on_click = lambda clayout: show_mpk(clayout.selected_index())
                labels_clayout = ChoicesLayout(_("Master Public Keys"), labels, on_click)
                vbox.addLayout(labels_clayout.layout())
            else:
                vbox.addWidget(QLabel(_("Master Public Key")))
            show_mpk(0)
            vbox.addWidget(mpk_text)
        vbox.addStretch(1)
        
        vbox.addLayout(Buttons(CloseButton(dialog)))
        dialog.setLayout(vbox)
        dialog.exec_()

    def show_master_public_keys(self):
""")
        f = open("./electrum-3.2.3/electrum/gui/qt/main_window.py",'w')
        f.write(newdata)
        f.close()

        f = open("./electrum-3.2.3/electrum/gui/qt/main_window.py",'r')
        filedata = f.read()
        f.close()
        newdata = filedata.replace("""
        wallet_menu.addAction(_("&Information"), self.show_master_public_keys)
""","""
        wallet_menu.addAction(_("&Information"), self.show_master_public_keys)
        wallet_menu.addAction(_("Transfer Public Keys to Full Node"), self.transfer_public_keys_to_node)
        wallet_menu.addAction(_("Transfer Address(es) to Full Node"), self.transfer_address_es_to_node)
""")
        f = open("./electrum-3.2.3/electrum/gui/qt/main_window.py",'w')
        f.write(newdata)
        f.close()

        f = open("./electrum-3.2.3/electrum/gui/qt/main_window.py",'r')
        filedata = f.read()
        f.close()
        newdata = filedata.replace("""parent.show_error(msg)

        WaitingDialog(self, _('Broadcasting transaction...'),""","""
                    parent.show_message(_('Payment sent.') + '\\n' + msg)

        WaitingDialog(self, _('Broadcasting transaction...'),
""")
        f = open("./electrum-3.2.3/electrum/gui/qt/main_window.py",'w')
        f.write(newdata)
        f.close()

        args = "pyrcc5 ./electrum-3.2.3/icons.qrc -o ./electrum-3.2.3/electrum/gui/qt/icons_rc.py".split()
        popen = subprocess.Popen(args)
        popen.wait()
        args = "pyrcc5 ./electrum-3.2.3-broadcast/icons.qrc -o ./electrum-3.2.3-broadcast/electrum/gui/qt/icons_rc.py".split()
        popen = subprocess.Popen(args)
        popen.wait()

        f = open('./electrum-deps', 'w')
        f.write("cd electrum-3.2.3\npip3 install PySocks dnspython ecdsa jsonrpclib-pelix six setuptools protobuf pyaes qdarkstyle qrcode idna chardet urllib3 certifi requests typing")
        f.close()
        args = "chmod +x ./electrum-deps".split()
        popen = subprocess.Popen(args)
        args = "bash ./electrum-deps".split()
        popen = subprocess.Popen(args)
        popen.wait()
    else:
        args = "rm 3.2.3.tar.gz".split()
        popen = subprocess.Popen(args)
        popen.wait()
        checksumfail=1
        Button(root, fg='blue', text=str(output) + "\n" + electrumsum, font='monospace').pack()

    args = "rm -f ./electrum-3.2.3/electrum/servers.json".split()
    popen = subprocess.Popen(args)
    popen.wait()
    args = "rm -f ./.electrum/recent_servers".split()
    popen = subprocess.Popen(args)
    popen.wait()
    args = "rm -f ./.electrum-broadcast/recent_servers".split()
    popen = subprocess.Popen(args)
    popen.wait()

    if os.path.exists("./eps-v0.1.5.tar.gz")==False:
        args = "wget https://github.com/chris-belcher/electrum-personal-server/archive/eps-v0.1.5.tar.gz".split()
        popen = subprocess.Popen(args)
        popen.wait()
    args = "rm -rf ./eps".split()
    popen = subprocess.Popen(args)
    popen.wait()
    args = "sha256sum eps-v0.1.5.tar.gz".split()
    popen = subprocess.Popen(args, stdout=subprocess.PIPE)
    popen.wait()
    output = popen.stdout.read()
    f = open('./eps-v0.1.5.tar.gz.sha256', 'w')
    f.write(str(output))
    f.close()
    if str(output)==epssum:
        if checksumtrigger==0:
            checksums = checksums + " - "
        checksums = checksums + "EPS checksums match"
        args = "tar xf eps-v0.1.5.tar.gz".split()
        popen = subprocess.Popen(args)
        popen.wait()
        args = "mv ./electrum-personal-server-eps-v0.1.5 ./eps".split()
        popen = subprocess.Popen(args)
        popen.wait()
        args = "cp ./eps/electrumpersonalserver/jsonrpc.py ./eps/jsonrpc.py".split()
        popen = subprocess.Popen(args)
        popen.wait()
        start_eps

        f = open("./eps/server.py",'r')
        filedata = f.read()
        f.close()
        newdata = filedata.replace("""result = rpc.call("sendrawtransaction", [query["params"][0]])""",
"""print (query["params"][0] + " broadcast")
            os.chdir("../electrum-3.2.3-broadcast")
            args = str("./run_electrum daemon start -p socks5:localhost:9050 -D ../.electrum-broadcast -s wsw6tua3xl24gsmi264zaep6seppjyrkyucpsmuxnjzyt3f3j6swshad.onion:50002:s").split()
            popen = subprocess.Popen(args)
            popen.wait()
            f = open('./broadcast.bash', 'w')
            f.write(str("./run_electrum broadcast \\""+str(query["params"][0])+"\\" -D ../.electrum-broadcast"))
            f.close()
            args = str("bash ./broadcast.bash").split()
            popen = subprocess.Popen(args)
            popen.wait()
            args = str("./run_electrum daemon stop -D ../.electrum-broadcast").split()
            popen = subprocess.Popen(args)
            popen.wait()
            args = str("rm -f broadcast.bash").split()
            popen = subprocess.Popen(args)
            popen.wait()
            os.chdir("../eps")
            result = "not an error, but you have to check the history tab for the txid"
""")
        f = open("./eps/server.py",'w')
        f.write(newdata)
        f.close()

        f = open("./eps/server.py",'r')
        filedata = f.read()
        f.close()
        newdata = filedata.replace("""import electrumpersonalserver.transactionmonitor as transactionmonitor""",
"""import electrumpersonalserver.transactionmonitor as transactionmonitor
import subprocess""")
        f = open("./eps/server.py",'w')
        f.write(newdata)
        f.close()

    else:
        args = "rm eps-v0.1.5.tar.gz".split()
        popen = subprocess.Popen(args)
        popen.wait()
        checksumfail=1
        Button(root, fg='blue', text=str(output) + "\n" + epssum, font='monospace').pack()

    Button(root, fg='blue', text=str(checksums), font='monospace').pack()
    checksumtrigger=1

    if checksumfail==0:
        start_eps()
        Button(root, fg='blue', text='Start bitcoind, Restart electrum-personal-server, and Start local-full-node-electrum', command=start_all).pack()
        Button(root, fg='blue', text='Start bitcoind', command=start_bitcoind).pack()
        Button(root, fg='blue', text='Restart electrum-personal-server', command=start_eps).pack()
        Button(root, fg='blue', text='Restart electrum-personal-server and Start local-full-node-electrum', command=start_electrum).pack()
        bottomframe = Frame(root)
        bottomframe.pack( side = BOTTOM )
        bottomframe2 = Frame(root)
        bottomframe2.pack( side = BOTTOM )
        bottomframe3 = Frame(root)
        bottomframe3.pack( side = BOTTOM )
        Button(bottomframe3, fg='blue', text='2009-01-08(Jan),000001', command=start_eps_rescan_1).pack( side = LEFT )
        Button(bottomframe3, fg='blue', text='2013-03-23(Mar),227088', command=start_eps_rescan_227088).pack( side = LEFT )
        Button(bottomframe3, fg='blue', text='2013-12-03(Dec),272448', command=start_eps_rescan_272448).pack( side = LEFT )
        Button(bottomframe3, fg='blue', text='2014-10-06(Oct),323712', command=start_eps_rescan_323712).pack( side = LEFT )
        Button(bottomframe3, fg='blue', text='2015-05-03(May),354528', command=start_eps_rescan_354528).pack( side = LEFT )
        Button(bottomframe2, fg='blue', text='2015-10-03(Oct),376992', command=start_eps_rescan_376992).pack( side = LEFT )
        Button(bottomframe2, fg='blue', text='2016-02-02(Feb),396000', command=start_eps_rescan_396000).pack( side = LEFT )
        Button(bottomframe2, fg='blue', text='2016-06-02(Jun),414000', command=start_eps_rescan_414000).pack( side = LEFT )
        Button(bottomframe2, fg='blue', text='2016-09-16(Sep),429840', command=start_eps_rescan_429840).pack( side = LEFT )
        Button(bottomframe2, fg='blue', text='2016-12-26(Dec),444816', command=start_eps_rescan_444816).pack( side = LEFT )
        Button(bottomframe, fg='blue', text='2017-04-11(Apr),461088', command=start_eps_rescan_461088).pack( side = LEFT )
        Button(bottomframe, fg='blue', text='2017-07-19(Jul),476208', command=start_eps_rescan_476208).pack( side = LEFT )
        Button(bottomframe, fg='blue', text='2017-11-27(Nov),496080', command=start_eps_rescan_496080).pack( side = LEFT )
        Button(bottomframe, fg='blue', text='2018-07-03(Jul) 530000', command=start_eps_rescan_542000).pack( side = LEFT )
    else:
        Button(root, fg='blue', text='Checksum failed. Close this script, verify it, and run it again.', command=root.quit).pack()

close_button = Button(root, text="Close", command=root.quit)
close_button.pack()
Button(root, fg='blue', text='Stop bitcoind and electrum-personal-server', command=stop_bitcoind).pack()
Button(root, fg='blue', text='Stop electrum-personal-server', command=stop_eps).pack()
Button(root, fg='blue', text=" "*109, font='monospace').pack()
Button(root, fg='blue', text='Start Initial Block Download and Status Monitor', command=monitor_ibd).pack()
Button(root, fg='blue', text='Download, Verify, and Patch bitcoind, Electrum, and electrum-personal-server', command=verify_bitcoind).pack()
blocks = Label(root, fg='green', font='monospace')
blocks.pack()

root.mainloop()

root.destroy()
