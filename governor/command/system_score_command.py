# -*- coding: utf-8 -*-

import functools
from typing import Dict, Any

import icon
from icon.data import (
    Address,
    RpcResponse,
    RpcRequest,
    str_to_object_by_type,
)
from icon.wallet import KeyWallet

from .. import result_type
from ..score.governance import create_client
from ..score.system import SystemScore
from ..utils import (
    resolve_url,
    resolve_nid,
    resolve_wallet,
    print_result,
    print_with_title,
    confirm_transaction,
)


def init(sub_parser, common_parent_parser, invoke_parent_parser):
    _init_get_stake(sub_parser, common_parent_parser)
    _init_get_prep(sub_parser, common_parent_parser)
    _init_get_delegation(sub_parser, common_parent_parser)

    _init_query_iscore(sub_parser, common_parent_parser)
    _init_claim_iscore(sub_parser, common_parent_parser, invoke_parent_parser)


def _init_get_stake(sub_parser, common_parent_parser):
    name = "getStake"
    desc = "getStake command of system score"

    score_parser = sub_parser.add_parser(
        name, parents=[common_parent_parser], help=desc
    )

    score_parser.add_argument("address", type=str, nargs="?", help="address")
    score_parser.set_defaults(func=_get_stake)


def _get_stake(args) -> int:
    address = Address.from_string(args.address)

    hooks = {"request": _print_request, "response": _print_response}
    score = _create_system_score(args, invoke=False)
    result: Dict[str, str] = score.get_stake(address, hooks=hooks)

    result: Dict[str, Any] = str_to_object_by_type(result_type.GET_STAKE, result)
    print_result(result)

    return 0


def _init_get_prep(sub_parser, common_parent_parser):
    name = "getPRep"
    desc = "getPRep command of system score"

    score_parser = sub_parser.add_parser(
        name, parents=[common_parent_parser], help=desc
    )

    score_parser.add_argument("address", type=str, nargs="?", help="address")
    score_parser.set_defaults(func=_get_prep)


def _get_prep(args) -> int:
    address = Address.from_string(args.address)

    hooks = {"request": _print_request, "response": _print_response}
    score = _create_system_score(args, invoke=False)
    result: Dict[str, str] = score.get_prep(address, hooks=hooks)

    result: Dict[str, Any] = str_to_object_by_type(result_type.GET_PREP, result)
    print_result(result)

    return 0


def _init_get_delegation(sub_parser, common_parent_parser):
    name = "getDelegation"
    desc = "getDelegation command of system score"

    score_parser = sub_parser.add_parser(
        name, parents=[common_parent_parser], help=desc
    )

    score_parser.add_argument("address", type=str, nargs="?", help="address")
    score_parser.set_defaults(func=_get_delegation)


def _get_delegation(args):
    address = Address.from_string(args.address)

    hooks = {"request": _print_request, "response": _print_response}
    score = _create_system_score(args, invoke=False)
    result: Dict[str, str] = score.get_delegation(address, hooks=hooks)

    result: Dict[str, Any] = str_to_object_by_type(result_type.GET_DELEGATION, result)
    print_result(result)

    return 0


def _init_query_iscore(sub_parser, common_parent_parser):
    name = "queryIScore"
    desc = "queryIScore command of system score"

    score_parser = sub_parser.add_parser(
        name, parents=[common_parent_parser], help=desc
    )

    score_parser.add_argument("address", type=str, nargs="?", help="address")
    score_parser.set_defaults(func=_query_iscore)


def _query_iscore(args) -> int:
    address = Address.from_string(args.address)

    hooks = {"request": _print_request, "response": _print_response}
    score = _create_system_score(args, invoke=False)
    result: Dict[str, str] = score.query_iscore(address, hooks=hooks)

    result: Dict[str, Any] = str_to_object_by_type(result_type.QUERY_ISCORE, result)
    result["loop"] = result["estimatedICX"]
    result["icx"] = result["loop"] / 10 ** 18
    del result["estimatedICX"]

    print_result(result)

    return 0


def _init_claim_iscore(sub_parser, common_parent_parser, invoke_parent_parser):
    name = "claimIScore"
    desc = "claimIScore command of system score"

    score_parser = sub_parser.add_parser(
        name, parents=[common_parent_parser, invoke_parent_parser], help=desc
    )

    score_parser.set_defaults(func=_claim_iscore)


def _claim_iscore(args) -> bytes:
    yes: bool = args.yes

    hooks = {"request": functools.partial(confirm_transaction, yes=yes)}
    score = _create_system_score(args, invoke=True)
    return score.claim_iscore(hooks=hooks)


def _print_request(request: RpcRequest) -> bool:
    print_with_title("Request", request)
    return True


def _print_response(response: RpcResponse) -> bool:
    print_with_title("Response", response)
    return True


def _create_system_score(args, invoke: bool) -> SystemScore:
    url: str = resolve_url(args.url)
    nid: int = resolve_nid(args.nid, args.url)

    client: icon.Client = create_client(url)

    if invoke:
        step_limit: int = args.step_limit
        estimate: bool = args.estimate
        wallet: KeyWallet = resolve_wallet(args)

        return SystemScore(
            client=client,
            owner=wallet,
            nid=nid,
            step_limit=step_limit,
            estimate=estimate
        )
    else:
        return SystemScore(client)
