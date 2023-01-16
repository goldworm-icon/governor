# -*- coding: utf-8 -*-
__all__ = ("BalanceCommand", "TotalSupplyCommand", "TransferCommand")

from typing import Union

import icon
from icon.builder import TransactionBuilder
from icon.data import Address
from icon.data.unit import loop_to_str
from icon.wallet import KeyWallet

from .command import Command
from ..utils import (
    add_keystore_argument,
    get_address_from_args,
    get_coin_from_string,
    get_hooks_from_args,
    print_result,
    resolve_nid,
    resolve_url,
    resolve_wallet,
)

TRANSFER_FEE = 12_500_000_000 * 100_000


class BalanceCommand(Command):
    def __init__(self):
        super().__init__(name="balance", readonly=True)

    def init(self, sub_parser, common_parent_parser, invoke_parent_parser):
        desc = "icx_getBalance"

        parser = sub_parser.add_parser(
            self.name, parents=[common_parent_parser], help=desc
        )
        parser.add_argument(
            "address", type=str, nargs="?", default=None, help="address"
        )
        add_keystore_argument(parser, required=False)
        parser.set_defaults(func=self._run)

    @classmethod
    def _run(cls, args) -> int:
        url: str = resolve_url(args.url)
        address: Address = get_address_from_args(args)
        hooks = get_hooks_from_args(args)

        if address:
            client: icon.Client = icon.create_client(url)
            balance: int = client.get_balance(address, hooks=hooks)
            print_result(f"Balance: {loop_to_str(balance)}, {hex(balance)}")
        else:
            print("Address not defined")

        return 0


class TotalSupplyCommand(Command):
    def __init__(self):
        super().__init__(name="totalSupply", readonly=True)

    def init(self, sub_parser, common_parent_parser, invoke_parent_parser):
        desc = "icx_getTotalSupply"

        parser = sub_parser.add_parser(
            self.name, parents=[common_parent_parser], help=desc
        )
        parser.set_defaults(func=self._run)

    @classmethod
    def _run(cls, args) -> int:
        url: str = resolve_url(args.url)
        hooks = get_hooks_from_args(args)
        client: icon.Client = icon.create_client(url)
        total_supply: int = client.get_total_supply(hooks=hooks)
        print_result(f"totalSupply: {loop_to_str(total_supply)}, {hex(total_supply)}")
        return 0


class TransferCommand(Command):
    def __init__(self):
        super().__init__(name="transfer", readonly=False)

    def init(self, sub_parser, common_parent_parser, invoke_parent_parser):
        desc = "transfer ICX"

        parser = sub_parser.add_parser(
            self.name,
            parents=[common_parent_parser, invoke_parent_parser],
            help=desc
        )

        parser.add_argument(
            "to", type=str, default=None, help="to address"
        )
        parser.add_argument(
            "value",
            type=str,
            default=0,
            help="value to transfer in loop. ex) 100 or 1e18"
        )
        parser.add_argument(
            "--all",
            action="store_true",
            help="Transfer all balances to 'to' address"
        )

        parser.set_defaults(func=self._run)

    @classmethod
    def _run(cls, args) -> Union[bytes, int]:
        url: str = resolve_url(args.url)
        nid: int = resolve_nid(args.nid, args.url)
        to: Address = Address.from_string(args.to)
        step_limit: int = max(args.step_limit, 100_000)
        transfer_all: bool = args.all
        hooks = get_hooks_from_args(args)

        client: icon.Client = icon.create_client(url)
        wallet: KeyWallet = resolve_wallet(args)

        if not transfer_all:
            value: int = get_coin_from_string(args.value)
        else:
            value: int = client.get_balance(wallet.address) - TRANSFER_FEE
        if not isinstance(value, int) or value <= 0:
            return -1

        builder = (
            TransactionBuilder()
            .nid(nid)
            .from_(wallet.address)
            .to(to)
            .value(value)
            .step_limit(step_limit)
        )

        return client.send_transaction(
            builder.build(),
            hooks=hooks,
            private_key=wallet.private_key
        )
