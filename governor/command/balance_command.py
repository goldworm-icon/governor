# -*- coding: utf-8 -*-

from abc import ABC

import icon
from icon.data import Address
from icon.data.unit import loop_to_str

from .command import Command
from ..utils import (
    get_address_from_args,
    print_request,
    print_response,
    print_result,
    resolve_url,
)


class BalanceCommand(Command, ABC):
    def __init__(self):
        self._name = "balance"

    def init(self, sub_parser, common_parent_parser, invoke_parent_parser):
        desc = "icx_getBalance"

        parser = sub_parser.add_parser(
            self._name, parents=[common_parent_parser], help=desc
        )

        parser.add_argument(
            "address", type=str, nargs="?", default=None, help="address"
        )
        parser.add_argument(
            "--keystore", "-k", type=str, required=False, help="keystore file path"
        )

        parser.set_defaults(func=self._run)

    @property
    def name(self) -> str:
        return self._name

    @classmethod
    def _run(cls, args) -> int:
        url: str = resolve_url(args.url)
        address: Address = get_address_from_args(args)

        if address:
            hooks = {"request": print_request, "response": print_response}
            client: icon.Client = icon.create_client(url)
            balance: int = client.get_balance(address, hooks=hooks)
            print_result(f"Balance: {loop_to_str(balance)}, {hex(balance)}")
        else:
            print("Address not defined")

        return 0
