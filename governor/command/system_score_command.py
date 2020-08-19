# -*- coding: utf-8 -*-

import functools
from typing import Dict

import icon
from icon.builder import (
    CallBuilder,
    CallTransactionBuilder,
    Transaction,
)
from icon.data import Address, SYSTEM_SCORE_ADDRESS
from icon.wallet import KeyWallet

from governor.score.governance import create_client
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
    address = Address.from_string(args.address)

    client: icon.Client = create_client(url)
    params: Dict[str, str] = (
        CallBuilder()
        .to(SYSTEM_SCORE_ADDRESS)
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
    address = Address.from_string(args.address)

    client: icon.Client = create_client(url)
    params: Dict[str, str] = (
        CallBuilder()
        .to(SYSTEM_SCORE_ADDRESS)
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
    address = Address.from_string(args.address)

    client: icon.Client = create_client(url)
    params: Dict[str, str] = (
        CallBuilder()
        .to(SYSTEM_SCORE_ADDRESS)
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
    address = Address.from_string(args.address)

    client: icon.Client = create_client(url)
    params: Dict[str, str] = (
        CallBuilder()
        .to(SYSTEM_SCORE_ADDRESS)
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
    wallet: KeyWallet = resolve_wallet(args)

    client: icon.Client = create_client(url)
    tx: Transaction = (
        CallTransactionBuilder()
        .nid(nid)
        .from_(wallet.address)
        .to(SYSTEM_SCORE_ADDRESS)
        .step_limit(step_limit)
        .call_data(method="claimIScore", params=None)
        .build()
    )

    hook = functools.partial(confirm_transaction, yes=yes)
    return client.send_transaction(
        tx, estimate=estimate, hooks={"request": hook}, private_key=wallet.private_key
    )
