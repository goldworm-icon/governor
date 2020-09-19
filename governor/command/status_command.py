# -*- coding: utf-8 -*-

# Copyright 2019 ICON Foundation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from typing import Dict

import icon
from icon.data import Address, RpcRequest, RpcResponse

from ..utils import (
    get_address_from_args,
    print_response,
    print_result,
    print_with_title,
    resolve_url,
)


def _print_request(request: RpcRequest) -> bool:
    print_with_title("Request", request)
    return True


def _print_response(response: RpcResponse) -> bool:
    print_with_title("Response", response)
    return True


def init(sub_parser, common_parent_parser, _invoke_parent_parser):
    _init_get_status(sub_parser, common_parent_parser)
    _init_get_balance(sub_parser, common_parent_parser)


def _init_get_status(sub_parser, common_parent_parser):
    name = "getStatus"
    desc = "ise_getStatus command"

    score_parser = sub_parser.add_parser(
        name, parents=[common_parent_parser], help=desc
    )

    score_parser.add_argument(
        "filter", type=str, nargs="?", help="filter ex) lastblock"
    )

    score_parser.set_defaults(func=_get_status)


def _get_status(args) -> int:
    url: str = resolve_url(args.url)
    _filter: str = args.filter

    client: icon.Client = icon.create_client(url)
    result: Dict[str, str] = client.get_status()
    print_response(f"{result}")

    return 0


def _init_get_balance(sub_parser, common_parent_parser):
    name = "getBalance"
    desc = "icx_getBalance"

    parser = sub_parser.add_parser(
        name, parents=[common_parent_parser], help=desc
    )

    parser.add_argument(
        "address", type=str, nargs="?", default=None, help="address"
    )
    parser.add_argument(
        "--keystore", "-k", type=str, required=False, help="keystore file path"
    )

    parser.set_defaults(func=_get_balance)


def _get_balance(args) -> int:
    url: str = resolve_url(args.url)
    address: Address = get_address_from_args(args)

    if address:
        hooks = {"request": _print_request, "response": _print_response}
        client: icon.Client = icon.create_client(url)
        balance: int = client.get_balance(address, hooks=hooks)
        print_result(f"Balance: {balance:_}, {hex(balance)}")
    else:
        print("Address not defined")

    return 0
