# -*- coding: utf-8 -*-

import os

import icon
from .command import Command


class WalletCommand(Command):
    def __init__(self):
        super().__init__(name="wallet", readonly=False)

    def init(self, sub_parser, common_parent_parser, invoke_parent_parser):
        desc = "Shows wallet information"

        parser = sub_parser.add_parser(
            self.name, parents=[common_parent_parser], help=desc
        )

        parser.add_argument(
            "path", type=str, nargs="?", default=None, help="keystore file path or private key in hex format"
        )
        parser.add_argument(
            "--password", type=str, nargs="?", default=None, help="keystore file path or private key in hex format"
        )

        parser.set_defaults(func=self._run)

    @classmethod
    def _run(cls, args) -> int:
        path = args.path

        if os.path.isfile(path):
            password = args.password
            if password is None:
                print("Password is needed")
                return 1

            wallet = icon.KeyWallet.load(path, password)
        else:
            private_key = path
            if private_key.startswith("0x"):
                private_key = private_key[2:]
            pri_key: bytes = bytes.fromhex(private_key)
            wallet = icon.KeyWallet(pri_key)

        print(
            f"address: {wallet.address}\n"
            f"pub_key: {wallet.public_key.hex()}\n"
            f"pri_key: {wallet.private_key.hex()}\n"
        )
        return 0
