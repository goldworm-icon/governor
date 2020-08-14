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
from ..governance import create_client
from ..utils import resolve_url, print_response, print_result


GET_STAKE_RESULT_TYPE = {
    "stake": int,
    "unstakes": [{"unstake": int, "unstakeBlockHeight": int, "remainingBlocks": int}]
}


def init(sub_parser, common_parent_parser, _invoke_parent_parser):
    _init_get_stake(sub_parser, common_parent_parser)


def _init_get_stake(sub_parser, common_parent_parser):
    name = "getstake"
    desc = "getStake command of system score"

    score_parser = sub_parser.add_parser(
        name, parents=[common_parent_parser], help=desc
    )

    score_parser.add_argument("address", type=str, nargs="?", help="address")
    score_parser.set_defaults(func=_get_stake)


def _get_stake(args) -> int:
    url: str = resolve_url(args.url)
    address = icon.Address.from_string(args.address)

    client: icon.Client = create_client(url)
    params: Dict[str, str] = (
        icon.CallBuilder("getStake")
        .to(icon.Address.from_int(icon.AddressPrefix.CONTRACT, 0))
        .params({"address": address})
        .build()
    )
    result: Dict[str, str] = client.call(params)
    print_result(GET_STAKE_RESULT_TYPE, result)

    return 0
