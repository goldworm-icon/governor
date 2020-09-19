# -*- coding: utf-8 -*-

from abc import ABC
from typing import Dict

import icon
from icon.data import Address

from .command import Command
from ..utils import (
    get_address_from_args,
    print_request,
    print_response,
    print_result,
    resolve_url,
)


class AccountCommand(Command, ABC):
    def __init__(self):
        self._name = "account"

    def init(self, sub_parser, common_parent_parser, invoke_parent_parser):
        desc = "debug_getAccount"

        parser = sub_parser.add_parser(
            self._name, parents=[common_parent_parser], help=desc
        )

        parser.add_argument(
            "address", type=str, nargs="?", default=None, help="address"
        )
        parser.add_argument(
            "--keystore", "-k", type=str, required=False, help="keystore file path"
        )
        parser.add_argument(
            "--filter",
            "-f",
            type=int,
            required=False,
            default=7,
            help="1(coin), 2(stake), 4(delegation) default(7)",
        )

        parser.set_defaults(func=self._run)

    @property
    def name(self) -> str:
        return self._name

    @classmethod
    def _run(cls, args) -> int:
        url: str = resolve_url(args.url)
        address: Address = get_address_from_args(args)
        _filter: int = args.filter

        if address:
            hooks = {"request": print_request, "response": print_response}
            client: icon.Client = icon.create_client(url)
            result: Dict[str, str] = client.get_account(address, _filter=_filter, hooks=hooks)
            print_result(result)
        else:
            print("Address not defined")

        return 0
