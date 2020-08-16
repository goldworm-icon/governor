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
from ..result_type import (
    GET_DELEGATION,
    GET_PREP,
    GET_STAKE,
    QUERY_ISCORE,
)
from ..utils import (
    resolve_url,
    resolve_nid,
    resolve_wallet,
    print_result,
    confirm_transaction,
)


def init(sub_parser, common_parent_parser, invoke_parent_parser):
    _init_get_stake(sub_parser, common_parent_parser)
    _init_get_prep(sub_parser, common_parent_parser)
    _init_get_delegation(sub_parser, common_parent_parser)

    _init_query_iscore(sub_parser, common_parent_parser)
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
        .to(icon.SYSTEM_SCORE_ADDRESS)
        .call_data(method="getStake", params={"address": address})
        .build()
    )
    result: Dict[str, str] = client.call(params)
    print_result(GET_STAKE, result)

    return 0


def _init_get_prep(sub_parser, common_parent_parser):
    name = "getprep"
    desc = "getPRep command of system score"

    score_parser = sub_parser.add_parser(
        name, parents=[common_parent_parser], help=desc
    )

    score_parser.add_argument("address", type=str, nargs="?", help="address")
    score_parser.set_defaults(func=_get_prep)


def _get_prep(args) -> int:
    url: str = resolve_url(args.url)
    address = icon.Address.from_string(args.address)

    client: icon.Client = create_client(url)
    params: Dict[str, str] = (
        icon.CallBuilder()
            .to(icon.SYSTEM_SCORE_ADDRESS)
            .call_data(method="getPRep", params={"address": address})
            .build()
    )
    result: Dict[str, str] = client.call(params)
    print_result(GET_PREP, result)

    return 0


def _init_get_delegation(sub_parser, common_parent_parser):
    name = "getdelegation"
    desc = "getDelegation command of system score"

    score_parser = sub_parser.add_parser(
        name, parents=[common_parent_parser], help=desc
    )

    score_parser.add_argument("address", type=str, nargs="?", help="address")
    score_parser.set_defaults(func=_get_delegation)


def _get_delegation(args):
    url: str = resolve_url(args.url)
    address = icon.Address.from_string(args.address)

    client: icon.Client = create_client(url)
    params: Dict[str, str] = (
        icon.CallBuilder()
            .to(icon.SYSTEM_SCORE_ADDRESS)
            .call_data(method="getDelegation", params={"address": address})
            .build()
    )
    result: Dict[str, str] = client.call(params)
    print_result(GET_DELEGATION, result)

    return 0


def _init_query_iscore(sub_parser, common_parent_parser):
    name = "queryiscore"
    desc = "queryIScore command of system score"

    score_parser = sub_parser.add_parser(
        name, parents=[common_parent_parser], help=desc
    )

    score_parser.add_argument("address", type=str, nargs="?", help="address")
    score_parser.set_defaults(func=_query_iscore)


def _query_iscore(args) -> int:
    url: str = resolve_url(args.url)
    address = icon.Address.from_string(args.address)

    client: icon.Client = create_client(url)
    params: Dict[str, str] = (
        icon.CallBuilder()
        .to(icon.SYSTEM_SCORE_ADDRESS)
        .call_data(method="queryIScore", params={"address": address})
        .build()
    )
    result: Dict[str, str] = client.call(params)
    print_result(QUERY_ISCORE, result)

    return 0


def _init_claim_iscore(sub_parser, common_parent_parser, invoke_parent_parser):
    name = "claimiscore"
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
        .to(icon.SYSTEM_SCORE_ADDRESS)
        .step_limit(step_limit)
        .call_data(method="claimIScore", params=None)
        .build()
    )

    if confirm_transaction(tx.to_dict(), yes):
        return client.send_transaction(tx, estimate)
