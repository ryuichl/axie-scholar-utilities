import json
import logging

from trezorlib.client import get_default_client
from trezorlib.tools import parse_path
from trezorlib import ethereum

from axie.utils import load_json
from trezor.trezor_utils import CustomUI
from trezorlib.ui import ClickUI


class TrezorAccountsSetup:
    
    def __init__(self, payments_file, trezor_config_file=None):
        self.trezor_config_file = trezor_config_file
        self.trezor_config = load_json(trezor_config_file) if trezor_config_file else {}
        self.payments = load_json(payments_file)

    def update_trezor_config(self):
        account_list = []
        for acc in self.payments['Scholars']:
            account_list.append(acc['AccountAddress'])
        
        non_configured_accs = account_list.copy()

        for tc in self.trezor_config:
            if tc in account_list:
                non_configured_accs.remove(tc)

        while non_configured_accs:
            print(non_configured_accs)
            pf = input("Please input one of your passphrases (can be empty): ")
            if pf:
                ui = CustomUI(passphrase=pf)
            else:
                ui = ClickUI()
            num_accs = 0
            while num_accs == 0:
                num_inp = input("Please input number of accounts in that passphrase (1-50): ")
                try:
                    num_accs = int(num_inp)
                except ValueError:
                    pass
            for i in range(num_accs):
                client = get_default_client(ui=ui)
                bip_path = f"m/44'/60'/0'/0/{i}"
                address = ethereum.get_address(client, parse_path(bip_path), True).replace('0x', 'ronin:')
                print(address, len(non_configured_accs))
                if address in non_configured_accs:
                    print('XXX')
                    if pf:
                        self.trezor_config[address] = {"passphrase": pf, "bip_path": bip_path}
                    else:
                        self.trezor_config[address] = {"passphrase": None, "bip_path": bip_path}
                    non_configured_accs.remove(address)
        
        file_path = self.trezor_config_file if self.trezor_config_file else 'trezor_config.json'
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(self.trezor_config, f, indent=4)     
