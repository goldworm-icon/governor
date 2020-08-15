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

from ..constants import ZERO_ADDRESS
from ..governance import create_client
from ..utils import (
    resolve_url,
    resolve_nid,
    resolve_wallet,
    print_result,
    confirm_transaction,
)

GET_STAKE_RESULT_TYPE = {
    "stake": int,
    "unstakes": [{"unstake": int, "unstakeBlockHeight": int, "remainingBlocks": int}],
}


def init(sub_parser, common_parent_parser, invoke_parent_parser):
    _init_get_stake(sub_parser, common_parent_parser)
    _init_claim_iscore(sub_parser, common_parent_parser, invoke_parent_parser)


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
        icon.CallBuilder()
        .to(ZERO_ADDRESS)
        .call_data(method="getStake", params={"address": address})
        .build()
    )
    result: Dict[str, str] = client.call(params)
    print_result(GET_STAKE_RESULT_TYPE, result)

    return 0


def _init_claim_iscore(sub_parser, common_parent_parser, invoke_parent_parser):
    name = "claim"
    desc = "claimIScore command provided by system score"

    score_parser = sub_parser.add_parser(
        name, parents=[common_parent_parser, invoke_parent_parser], help=desc
    )

    score_parser.set_defaults(func=_claim_iscore)


def _claim_iscore(args) -> bytes:
    url: str = resolve_url(args.url)
    nid: int = resolve_nid(args.nid, args.url)
    step_limit: int = args.step_limit
    yes: bool = args.yes
    estimate: bool = args.estimate
    wallet: icon.KeyWallet = resolve_wallet(args)

    client: icon.Client = create_client(url)
    tx: icon.builder.Transaction = (
        icon.CallTransactionBuilder()
        .nid(nid)
        .from_(wallet.address)
        .to(ZERO_ADDRESS)
        .step_limit(step_limit)
        .call_data(method="claimIScore", params=None)
        .build()
    )

    if confirm_transaction(tx.to_dict(), yes):
        return client.send_transaction(tx, estimate)
