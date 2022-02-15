# -*- coding: utf-8 -*-
__all__ = ("WalletCommand", "CreateWalletCommand")

import os

import icon
from icon.utils import hex_to_bytes
from .command import Command
from .. import utils


class WalletCommand(Command):
    def __init__(self):
        super().__init__(name="wallet", readonly=True)

    def init(self, sub_parser, common_parent_parser, invoke_parent_parser):
        desc = "Shows wallet information"

        parser = sub_parser.add_parser(self.name, help=desc)
        parser.add_argument(
            "path", type=str, default=None, help="keystore file path or private key in hex format"
        )
        utils.add_password_argument(parser)
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
            private_key: str = path
            pri_key: bytes = hex_to_bytes(private_key)
            wallet = icon.KeyWallet(pri_key)

        _print_wallet_info(wallet)
        return 0


class CreateWalletCommand(Command):
    def __init__(self):
        super().__init__(name="createWallet", readonly=True)

    def init(self, sub_parser, common_parent_parser, invoke_parent_parser):
        desc = "Create a keystore file from private key"

        parser = sub_parser.add_parser(self.name, help=desc)
        parser.add_argument(
            "path", type=str, default=None, help="keystore file path"
        )
        parser.add_argument(
            "--private-key", type=str, nargs="?", default=None, help="private key in hex format. [ex: 0xdeadbeef...]"
        )
        utils.add_password_argument(parser)
        parser.set_defaults(func=self._run)

    @classmethod
    def _run(cls, args) -> int:
        path = args.path
        password: str = utils.get_password(args.password)
        pri_key: bytes = hex_to_bytes(args.private_key)
        wallet = icon.KeyWallet(pri_key)
        wallet.save(path, password)
        _print_wallet_info(wallet)
        return 0


def _print_wallet_info(wallet: icon.Wallet):
    print(
        f"address: {wallet.address}\n"
        f"pub_key: {wallet.public_key.hex()}\n"
        f"pri_key: {wallet.private_key.hex()}\n"
    )
