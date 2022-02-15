# -*- coding: utf-8 -*-

__all__ = (
    "BondCommand",
    "BonderListCommand",
    "ClaimIScoreCommand",
    "DelegationCommand",
    "IISSInfoCommand",
    "IScoreCommand",
    "MainPRepsCommand",
    "NetworkInfoCommand",
    "PRepCommand",
    "PRepsCommand",
    "PRepStatsCommand",
    "ScoreOwnerCommand",
    "SetBonderListCommand",
    "SetStakeCommand",
    "StakeCommand",
    "SubPRepsCommand",
    "SystemRevisionCommand",
    "TermCommand",
)

import functools
from typing import Dict, Any, List

import icon
from icon.data import Address
from icon.data.unit import loop_to_str
from icon.utils import str_to_object_by_type
from icon.wallet import KeyWallet
from .command import Command
from .. import result_type
from ..score.system import SystemScore
from ..utils import (
    add_keystore_argument,
    confirm_transaction,
    get_address_from_args,
    print_result,
    print_request,
    print_response,
    resolve_nid,
    resolve_url,
    resolve_wallet,
)


class StakeCommand(Command):
    def __init__(self):
        super().__init__(name="stake", readonly=True)
        self._hooks = {"request": print_request, "response": print_response}

    def init(self, sub_parser, common_parent_parser, invoke_parent_parser):
        desc = "getStake command of system score"

        parser = sub_parser.add_parser(
            self.name, parents=[common_parent_parser], help=desc
        )

        parser.add_argument("address", type=str, nargs="?", help="address")
        add_keystore_argument(parser, required=False)
        parser.set_defaults(func=self._run)

    def _run(self, args) -> int:
        address: Address = get_address_from_args(args)

        score = _create_system_score(args, invoke=False)
        result: Dict[str, str] = score.get_stake(address, hooks=self._hooks)
        self._print_result(result)

        return 0

    @classmethod
    def _print_result(cls, result: Dict[str, str]):
        result: Dict[str, Any] = str_to_object_by_type(
            result_type.GET_STAKE, result
        )

        result["stake"] = loop_to_str(result["stake"])

        print_result(result)


class SetStakeCommand(Command):
    def __init__(self):
        super().__init__(name="setStake", readonly=False)
        self._hooks = {"request": print_request, "response": print_response}

    def init(self, sub_parser, common_parent_parser, invoke_parent_parser):
        desc = "setStake command of system score"

        parser = sub_parser.add_parser(
            self.name, parents=[common_parent_parser], help=desc
        )

        parser.add_argument("stake", type=int, help="stake")
        parser.set_defaults(func=self._run)

    def _run(self, args) -> bytes:
        score = _create_system_score(args, invoke=True)
        return score.set_stake(args.stake, hooks=self._hooks)


class PRepCommand(Command):
    def __init__(self):
        super().__init__(name="prep", readonly=True)
        self._hooks = {"request": print_request, "response": print_response}

    def init(self, sub_parser, common_parent_parser, invoke_parent_parser):
        desc = "getPRep command of system score"

        parser = sub_parser.add_parser(
            self.name, parents=[common_parent_parser], help=desc
        )

        parser.add_argument("address", type=str, nargs="?", help="address")
        add_keystore_argument(parser, required=False)
        parser.set_defaults(func=self._run)

    def _run(self, args) -> int:
        address: Address = get_address_from_args(args)

        score = _create_system_score(args, invoke=False)
        result: Dict[str, str] = score.get_prep(address, hooks=self._hooks)

        result: Dict[str, Any] = str_to_object_by_type(result_type.GET_PREP, result)
        print_result(result)

        return 0


class PRepsCommand(Command):
    def __init__(self):
        super().__init__(name="preps", readonly=True)
        self._hooks = {"request": print_request, "response": print_response}

    def init(self, sub_parser, common_parent_parser, invoke_parent_parser):
        desc = "getPReps command of system score"

        parser = sub_parser.add_parser(
            self.name, parents=[common_parent_parser], help=desc
        )

        parser.add_argument(
            "--start", type=int, nargs="?", default=0, help="start ranking"
        )
        parser.add_argument(
            "--end", type=int, nargs="?", default=0, help="end ranking"
        )
        parser.add_argument(
            "--height", type=int, default=-1, help="block height to query"
        )
        parser.set_defaults(func=self._run)

    def _run(self, args) -> int:
        start: int = args.start
        end: int = args.end
        height: int = args.height

        score = _create_system_score(args, invoke=False)
        result: Dict[str, str] = score.get_preps(start, end, height, hooks=self._hooks)

        result: Dict[str, Any] = str_to_object_by_type(result_type.GET_PREPS, result)
        print_result(result)

        return 0


class MainPRepsCommand(Command):
    def __init__(self):
        super().__init__(name="mainpreps", readonly=True)
        self._hooks = {"request": print_request, "response": print_response}

    def init(self, sub_parser, common_parent_parser, invoke_parent_parser):
        desc = "getMainPReps command of system score"

        parser = sub_parser.add_parser(
            self.name, parents=[common_parent_parser], help=desc
        )
        parser.add_argument(
            "--height", type=int, default=-1, help="block height to query"
        )
        parser.set_defaults(func=self._run)

    def _run(self, args) -> int:
        height: int = args.height
        score = _create_system_score(args, invoke=False)
        result: Dict[str, str] = score.get_main_preps(height, hooks=self._hooks)
        print_result(result)

        return 0


class SubPRepsCommand(Command):
    def __init__(self):
        super().__init__(name="subpreps", readonly=True)
        self._hooks = {"request": print_request, "response": print_response}

    def init(self, sub_parser, common_parent_parser, invoke_parent_parser):
        desc = "getSubPReps command of system score"

        parser = sub_parser.add_parser(
            self.name, parents=[common_parent_parser], help=desc
        )

        parser.set_defaults(func=self._run)

    def _run(self, args) -> int:
        score = _create_system_score(args, invoke=False)
        result: Dict[str, str] = score.get_prep_stats(hooks=self._hooks)
        print_result(result)

        return 0


class PRepStatsCommand(Command):
    def __init__(self):
        super().__init__(name="prepStats", readonly=True)
        self._hooks = {"request": print_request, "response": print_response}

    def init(self, sub_parser, common_parent_parser, invoke_parent_parser):
        desc = "getPRepStats command of system score"

        parser = sub_parser.add_parser(
            self.name, parents=[common_parent_parser], help=desc
        )
        parser.set_defaults(func=self._run)

    def _run(self, args) -> int:
        score = _create_system_score(args, invoke=False)
        result: Dict[str, str] = score.get_prep_stats(hooks=self._hooks)

        result: Dict[str, Any] = str_to_object_by_type(result_type.GET_PREP_STATS, result)
        print_result(result)
        return 0


class DelegationCommand(Command):
    def __init__(self):
        super().__init__(name="delegation", readonly=True)
        self._hooks = {"request": print_request, "response": print_response}

    def init(self, sub_parser, common_parent_parser, invoke_parent_parser):
        desc = "getDelegation command of system score"

        parser = sub_parser.add_parser(
            self.name, parents=[common_parent_parser], help=desc
        )

        parser.add_argument("address", type=str, nargs="?", help="address")
        add_keystore_argument(parser, required=False)
        parser.set_defaults(func=self._run)

    def _run(self, args) -> int:
        address: Address = get_address_from_args(args)

        score = _create_system_score(args, invoke=False)
        result: Dict[str, str] = score.get_delegation(address, hooks=self._hooks)

        result: Dict[str, Any] = str_to_object_by_type(
            result_type.GET_DELEGATION, result
        )
        loop: int = result["totalDelegated"]
        result["totalDelegated"] = loop_to_str(loop)

        print_result(result)

        return 0


class IScoreCommand(Command):
    def __init__(self):
        super().__init__(name="iscore", readonly=True)
        self._hooks = {"request": print_request, "response": print_response}

    def init(self, sub_parser, common_parent_parser, invoke_parent_parser):
        desc = "queryIScore command of system score"

        parser = sub_parser.add_parser(
            self.name, parents=[common_parent_parser], help=desc
        )

        parser.add_argument("address", type=str, nargs="?", help="address")
        parser.add_argument(
            "--keystore", "-k", type=str, required=False, help="keystore file path"
        )
        parser.set_defaults(func=self._run)

    def _run(self, args) -> int:
        address: Address = get_address_from_args(args)

        score = _create_system_score(args, invoke=False)
        result: Dict[str, str] = score.query_iscore(address, hooks=self._hooks)
        self._print_result(result)

        return 0

    @classmethod
    def _print_result(cls, result: Dict[str, str]):
        result: Dict[str, Any] = str_to_object_by_type(
            result_type.QUERY_ISCORE, result
        )

        key = "estimatedICX"
        result[key] = loop_to_str(result[key])

        print_result(result)


class ClaimIScoreCommand(Command):
    def __init__(self):
        super().__init__(name="claimIScore", readonly=False)
        self._hooks = {"request": print_request, "response": print_response}

    def init(self, sub_parser, common_parent_parser, invoke_parent_parser):
        desc = "claimIScore command of system score"

        parser = sub_parser.add_parser(
            self.name,
            parents=[common_parent_parser, invoke_parent_parser],
            help=desc
        )

        parser.set_defaults(func=self._run)

    @classmethod
    def _run(cls, args) -> bytes:
        yes: bool = args.yes

        hooks = {
            "request": [
                functools.partial(confirm_transaction, yes=yes),
                print_request,
            ],
            "response": print_response,
        }
        score = _create_system_score(args, invoke=True)
        return score.claim_iscore(hooks=hooks)


def _create_system_score(args, invoke: bool) -> SystemScore:
    url: str = resolve_url(args.url)
    nid: int = resolve_nid(args.nid, args.url)

    client: icon.Client = icon.create_client(url)

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


class BonderListCommand(Command):
    def __init__(self):
        super().__init__(name="bonderList", readonly=True)
        self._hooks = {"request": print_request, "response": print_response}

    def init(self, sub_parser, common_parent_parser, invoke_parent_parser):
        desc = "getBonderList command of system score"

        parser = sub_parser.add_parser(
            self.name, parents=[common_parent_parser], help=desc
        )

        parser.add_argument("address", type=str, nargs="?", help="address")
        add_keystore_argument(parser, required=False)
        parser.set_defaults(func=self._run)

    def _run(self, args) -> int:
        address: Address = get_address_from_args(args)

        score = _create_system_score(args, invoke=False)
        result: Dict[str, str] = score.get_bonder_list(address, hooks=self._hooks)
        print_result(result)

        return 0


class BondCommand(Command):
    def __init__(self):
        super().__init__(name="bond", readonly=True)
        self._hooks = {"request": print_request, "response": print_response}

    def init(self, sub_parser, common_parent_parser, invoke_parent_parser):
        desc = "getBond command of system score"

        parser = sub_parser.add_parser(
            self.name, parents=[common_parent_parser], help=desc
        )

        parser.add_argument("address", type=str, nargs="?", help="address")
        add_keystore_argument(parser, required=False)
        parser.set_defaults(func=self._run)

    def _run(self, args) -> int:
        address: Address = get_address_from_args(args)

        score = _create_system_score(args, invoke=False)
        result: Dict[str, str] = score.get_bond(address, hooks=self._hooks)
        print_result(result)

        return 0


class IISSInfoCommand(Command):
    def __init__(self):
        super().__init__(name="iissInfo", readonly=True)
        self._hooks = {"request": print_request, "response": print_response}

    def init(self, sub_parser, common_parent_parser, invoke_parent_parser):
        desc = "getIISSInfo command of system score"

        parser = sub_parser.add_parser(
            self.name, parents=[common_parent_parser], help=desc
        )

        parser.set_defaults(func=self._run)

    def _run(self, args) -> int:
        score = _create_system_score(args, invoke=False)
        result: Dict[str, str] = score.get_iiss_info(self._hooks)
        print_result(result)

        return 0


class SetBonderListCommand(Command):
    def __init__(self):
        super().__init__(name="setBonderList", readonly=False)
        self._hooks = {"request": print_request, "response": print_response}

    def init(self, sub_parser, common_parent_parser, invoke_parent_parser):
        desc = "setBonderList command of system score."

        parser = sub_parser.add_parser(
            self.name,
            parents=[common_parent_parser, invoke_parent_parser],
            help=desc
        )

        parser.add_argument(
            "addresses",
            type=str,
            nargs="?",
            default="",
            help="addresses ex) addr1,addr2,...")
        parser.set_defaults(func=self._run)

    @classmethod
    def _run(cls, args) -> bytes:
        yes: bool = args.yes
        addresses = cls._to_address_list(args.addresses)

        hooks = {
            "request": [
                functools.partial(confirm_transaction, yes=yes),
                print_request,
            ],
            "response": print_response,
        }
        score = _create_system_score(args, invoke=True)
        return score.set_bonder_list(addresses, hooks=hooks)

    @classmethod
    def _to_address_list(cls, addresses: str) -> List[Address]:
        if addresses == "":
            return []

        return [
            Address.from_string(address)
            for address in addresses.split(",")
        ]


class SystemRevisionCommand(Command):
    def __init__(self):
        super().__init__(name="sysRevision", readonly=True)
        self._hooks = {"request": print_request, "response": print_response}

    def init(self, sub_parser, common_parent_parser, invoke_parent_parser):
        desc = "Call getRevision of system score. goloop only"

        parser = sub_parser.add_parser(
            self.name, parents=[common_parent_parser], help=desc
        )

        parser.set_defaults(func=self._run)

    def _run(self, args) -> int:
        score = _create_system_score(args, invoke=False)
        revision: int = score.get_revision(self._hooks)
        print_result(revision)

        return 0


class TermCommand(Command):
    def __init__(self):
        super().__init__(name="term", readonly=True)
        self._hooks = {"request": print_request, "response": print_response}

    def init(self, sub_parser, common_parent_parser, invoke_parent_parser):
        desc = "Display term info"

        parser = sub_parser.add_parser(
            self.name, parents=[common_parent_parser], help=desc
        )

        parser.set_defaults(func=self._run)

    def _run(self, args) -> int:
        score = _create_system_score(args, invoke=False)
        result: Dict[str, str] = score.get_prep_term(self._hooks)
        print_result(result)

        return 0


class ScoreOwnerCommand(Command):
    def __init__(self):
        super().__init__(name="scoreOwner", readonly=True)
        self._hooks = {"request": print_request, "response": print_response}

    def init(self, sub_parser, common_parent_parser, invoke_parent_parser):
        desc = "Display the owner of a given score"

        parser = sub_parser.add_parser(
            self.name, parents=[common_parent_parser], help=desc
        )
        parser.add_argument("address", type=str, nargs="?", help="score address")
        parser.set_defaults(func=self._run)

    def _run(self, args) -> int:
        score = _create_system_score(args, invoke=False)
        address: Address = get_address_from_args(args)

        owner: Address = score.get_score_owner(address, self._hooks)
        print_result(owner)

        return 0


class NetworkInfoCommand(Command):
    def __init__(self):
        super().__init__(name="networkInfo", readonly=True)
        self._hooks = {"request": print_request, "response": print_response}

    def init(self, sub_parser, common_parent_parser, invoke_parent_parser):
        desc = "Display network information"

        parser = sub_parser.add_parser(
            self.name, parents=[common_parent_parser], help=desc
        )
        parser.set_defaults(func=self._run)

    def _run(self, args) -> int:
        score = _create_system_score(args, invoke=False)
        ret = score.get_network_info(self._hooks)
        print_result(ret)
        return 0
