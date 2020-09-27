# -*- coding: utf-8 -*-

import functools
from typing import Union, Dict

import icon
from icon.data import Address
from icon.data.utils import hex_to_bytes
from icon.wallet import KeyWallet

from .command import Command
from ..score.governance import GovernanceScore
from ..utils import (
    confirm_transaction,
    get_address_from_args,
    print_request,
    print_response,
    print_result,
    resolve_nid,
    resolve_url,
    resolve_wallet,
)


class DeployCommand(Command):
    def __init__(self):
        super().__init__(name="deploy", readonly=False)

    def init(self, sub_parser, common_parent_parser, invoke_parent_parser):
        desc = "Install or update governance SCORE"

        score_parser = sub_parser.add_parser(
            self.name,
            parents=[common_parent_parser, invoke_parent_parser],
            help=desc
        )

        score_parser.add_argument(
            "score_path",
            type=str,
            nargs="?",
            help="path where governance SCORE is located\nex) ./governance",
        )

        score_parser.set_defaults(func=self._run)

    def _run(self, args) -> Union[int, str]:
        hooks = {
            "request": functools.partial(confirm_transaction, yes=args.yes),
            "response": print_response
        }

        score_path: str = args.score_path
        score = _create_governance_score(args, invoke=not self.readonly)
        return score.deploy(score_path, hooks=hooks)


class ScoreStatusCommand(Command):
    def __init__(self):
        super().__init__(name="scoreStatus", readonly=True)

    def init(self, sub_parser, common_parent_parser, invoke_parent_parser):
        desc = f"getScoreStatus command of governance score"

        score_parser = sub_parser.add_parser(
            self.name, parents=[common_parent_parser], help=desc
        )

        score_parser.add_argument(
            "address",
            type=str,
            nargs="?",
            help="SCORE address ex) cx8a96c0dcf0567635309809d391908c32fbca5317",
        )

        score_parser.set_defaults(func=self._run)

    def _run(self, args) -> int:
        hooks = {"request": print_request, "response": print_response}
        address: Address = get_address_from_args(args)

        score = _create_governance_score(args, invoke=not self.readonly)
        result: Dict[str, str] = score.get_score_status(address, hooks=hooks)
        print_response(result)

        return 0


class ServiceConfigCommand(Command):
    def __init__(self):
        super().__init__(name="serviceConfig", readonly=True)

    def init(self, sub_parser, common_parent_parser, invoke_parent_parser):
        desc = f"getServiceConfig command of governance score"

        score_parser = sub_parser.add_parser(
            self.name, parents=[common_parent_parser], help=desc
        )

        score_parser.set_defaults(func=self._run)

    def _run(self, args) -> int:
        hooks = {"request": print_request, "response": print_response}
        score = _create_governance_score(args, invoke=not self.readonly)
        result: Dict[str, str] = score.get_service_config(hooks=hooks)
        print_response(result)

        return 0


class UpdateServiceConfigCommand(Command):
    def __init__(self):
        super().__init__(name="updateServiceConfig", readonly=False)

    def init(self, sub_parser, common_parent_parser, invoke_parent_parser):
        desc = f"{self.name} command of governance score"

        score_parser = sub_parser.add_parser(
            self.name,
            parents=[common_parent_parser, invoke_parent_parser],
            help=desc
        )

        score_parser.add_argument("service_flag", type=int, nargs="?", help="")
        score_parser.set_defaults(func=self._run)

    def _run(self, args):
        hooks = {
            "request": functools.partial(confirm_transaction, yes=args.yes),
            "response": print_response
        }

        service_flag: int = args.service_flag
        score = _create_governance_score(args, invoke=not self.readonly)
        return score.update_service_config(service_flag, hooks=hooks)


class AcceptScoreCommand(Command):
    def __init__(self):
        super().__init__(name="acceptScore", readonly=False)

    def init(self, sub_parser, common_parent_parser, invoke_parent_parser):
        desc = f"{self.name} command of governance score"

        score_parser = sub_parser.add_parser(
            self.name,
            parents=[common_parent_parser, invoke_parent_parser],
            help=desc
        )

        score_parser.add_argument(
            "tx_hash",
            type=str,
            nargs="?",
            help="txHash ex) 0xe2a8e2483736ba8793bebebc30673aa4fb7662763bcdc7b0d4d8a163a79c9e20",
        )

        score_parser.set_defaults(func=self._run)

    def _run(self, args) -> Union[bytes, int]:
        hooks = {
            "request": functools.partial(confirm_transaction, yes=args.yes),
            "response": print_response
        }

        tx_hash: bytes = hex_to_bytes(args.tx_hash)
        score = _create_governance_score(args, invoke=not self.readonly)
        return score.accept_score(tx_hash, hooks=hooks)


class RejectScoreCommand(Command):
    def __init__(self):
        super().__init__(name="rejectScore", readonly=False)

    def init(self, sub_parser, common_parent_parser, invoke_parent_parser):
        desc = f"{self.name} command of governance score"

        score_parser = sub_parser.add_parser(
            self.name,
            parents=[common_parent_parser, invoke_parent_parser],
            help=desc
        )

        score_parser.add_argument(
            "tx_hash",
            type=str,
            nargs="?",
            help="txHash ex) 0xe2a8e2483736ba8793bebebc30673aa4fb7662763bcdc7b0d4d8a163a79c9e20",
        )

        score_parser.add_argument(
            "reason", type=str, nargs="?", help="reason ex) 'SCORE cannot use file API'"
        )

        score_parser.set_defaults(func=self._run)

    def _run(self, args) -> Union[bytes, int]:
        hooks = {
            "request": functools.partial(confirm_transaction, yes=args.yes),
            "response": print_response
        }

        tx_hash: bytes = hex_to_bytes(args.tx_hash)
        reason: str = args.reason

        score = _create_governance_score(args, invoke=not self.readonly)
        return score.reject_score(tx_hash, reason, hooks=hooks)


class AddAuditorCommand(Command):
    def __init__(self):
        super().__init__(name="addAuditor", readonly=False)

    def init(self, sub_parser, common_parent_parser, invoke_parent_parser):
        desc = f"{self.name} command of governance score"

        score_parser = sub_parser.add_parser(
            self.name,
            parents=[common_parent_parser, invoke_parent_parser],
            help=desc
        )

        score_parser.add_argument("address", type=str, nargs="?", help="")
        score_parser.set_defaults(func=self._run)

    def _run(self, args) -> Union[bytes, int]:
        hooks = {
            "request": functools.partial(confirm_transaction, yes=args.yes),
            "response": print_response
        }

        address: Address = get_address_from_args(args)
        score = _create_governance_score(args, invoke=not self.readonly)
        return score.add_auditor(address, hooks=hooks)


class RemoveAuditorCommand(Command):
    def __init__(self):
        super().__init__(name="removeAuditor", readonly=False)

    def init(self, sub_parser, common_parent_parser, invoke_parent_parser):
        desc = f"{self.name} command of governance score"

        score_parser = sub_parser.add_parser(
            self.name,
            parents=[common_parent_parser, invoke_parent_parser],
            help=desc
        )

        score_parser.add_argument("address", type=str, nargs="?", help="")
        score_parser.set_defaults(func=self._run)

    def _run(self, args) -> Union[bytes, int]:
        hooks = {
            "request": functools.partial(confirm_transaction, yes=args.yes),
            "response": print_response
        }

        address: Address = get_address_from_args(args)
        score = _create_governance_score(args, invoke=not self.readonly)
        return score.remove_auditor(address, hooks=hooks)


class AddToScoreBlackListCommand(Command):
    def __init__(self):
        super().__init__(name="addToScoreBlackList", readonly=False)

    def init(self, sub_parser, common_parent_parser, invoke_parent_parser):
        desc = f"{self.name} command"

        score_parser = sub_parser.add_parser(
            self.name,
            parents=[common_parent_parser, invoke_parent_parser],
            help=desc
        )

        score_parser.add_argument("address", type=str, nargs="?", help="")
        score_parser.set_defaults(func=self._run)

    def _run(self, args) -> Union[bytes, int]:
        hooks = {
            "request": functools.partial(confirm_transaction, yes=args.yes),
            "response": print_response
        }

        address: Address = get_address_from_args(args)
        score = _create_governance_score(args, invoke=not self.readonly)
        return score.add_to_score_black_list(address, hooks=hooks)


class RemoveFromScoreBlackListCommand(Command):
    def __init__(self):
        super().__init__(name="removeFromScoreBlackList", readonly=False)

    def init(self, sub_parser, common_parent_parser, invoke_parent_parser):
        desc = f"{self.name} command"

        score_parser = sub_parser.add_parser(
            self.name,
            parents=[common_parent_parser, invoke_parent_parser],
            help=desc
        )

        score_parser.add_argument("address", type=str, nargs="?", help="")
        score_parser.set_defaults(func=self._run)

    def _run(self, args) -> Union[bytes, int]:
        hooks = {
            "request": functools.partial(confirm_transaction, yes=args.yes),
            "response": print_response
        }

        address: Address = get_address_from_args(args)
        score = _create_governance_score(args, invoke=not self.readonly)
        return score.remove_from_score_black_list(address, hooks=hooks)


class AddImportWhiteListCommand(Command):
    def __init__(self):
        super().__init__(name="addImportWhiteList", readonly=False)

    def init(self, sub_parser, common_parent_parser, invoke_parent_parser):
        desc = f"{self.name} command of governance score"

        score_parser = sub_parser.add_parser(
            self.name,
            parents=[common_parent_parser, invoke_parent_parser],
            help=desc
        )

        score_parser.add_argument("import_stmt", type=str, nargs="?", help="")
        score_parser.set_defaults(func=self._run)

    def _run(self, args) -> Union[bytes, int]:
        hooks = {
            "request": functools.partial(confirm_transaction, yes=args.yes),
            "response": print_response
        }

        import_stmt: str = args.import_stmt
        score = _create_governance_score(args, invoke=not self.readonly)
        return score.add_import_white_list(import_stmt, hooks=hooks)


class RemoveImportWhiteListCommand(Command):
    def __init__(self):
        super().__init__(name="removeImportWhiteList", readonly=False)

    def init(self, sub_parser, common_parent_parser, invoke_parent_parser):
        desc = f"{self.name} command of governance score"

        score_parser = sub_parser.add_parser(
            self.name,
            parents=[common_parent_parser, invoke_parent_parser],
            help=desc
        )

        score_parser.add_argument("import_stmt", type=str, nargs="?", help="")
        score_parser.set_defaults(func=self._run)

    def _run(self, args) -> Union[bytes, int]:
        hooks = {
            "request": functools.partial(confirm_transaction, yes=args.yes),
            "response": print_response
        }

        import_stmt: str = args.import_stmt
        score = _create_governance_score(args, invoke=not self.readonly)
        return score.remove_import_white_list(import_stmt, hooks=hooks)


class InScoreBlackListCommand(Command):
    def __init__(self):
        super().__init__(name="inScoreBlackList", readonly=True)

    def init(self, sub_parser, common_parent_parser, invoke_parent_parser):
        desc = f"{self.name} command of governance score"

        score_parser = sub_parser.add_parser(
            self.name, parents=[common_parent_parser], help=desc
        )
        score_parser.add_argument("address", type=str, nargs="?", help="")
        score_parser.set_defaults(func=self._run)

    def _run(self, args) -> int:
        hooks = {"request": print_request, "response": print_response}

        address: Address = get_address_from_args(args)
        score = _create_governance_score(args, invoke=not self.readonly)
        is_score_in_black_list: bool = score.is_in_score_black_list(address, hooks=hooks)

        if is_score_in_black_list:
            print_result(f"{address} is blocked")
        else:
            print_result(f"{address} is not blocked")

        return 0


class InImportWhiteListCommand(Command):
    def __init__(self):
        super().__init__(name="inImportWhiteList", readonly=True)

    def init(self, sub_parser, common_parent_parser, invoke_parent_parser):
        desc = f"{self.name} command of governance score"

        score_parser = sub_parser.add_parser(
            self.name, parents=[common_parent_parser], help=desc
        )

        score_parser.add_argument("import_stmt", type=str, nargs="?", help="")
        score_parser.set_defaults(func=self._run)

    def _run(self, args) -> int:
        hooks = {"request": print_request, "response": print_response}

        import_stmt: str = args.import_stmt
        score = _create_governance_score(args, invoke=not self.readonly)
        in_whitelist: bool = score.is_in_import_white_list(import_stmt, hooks=hooks)

        print_result(f"{import_stmt} is {'allowed' if in_whitelist else 'denied'}")

        return 0


def _create_governance_score(args, invoke: bool) -> GovernanceScore:
    url: str = resolve_url(args.url)
    nid: int = resolve_nid(args.nid, args.url)

    client: icon.Client = icon.create_client(url)

    if invoke:
        step_limit: int = args.step_limit
        estimate: bool = args.estimate
        wallet: KeyWallet = resolve_wallet(args)

        return GovernanceScore(
            client=client,
            owner=wallet,
            nid=nid,
            step_limit=step_limit,
            estimate=estimate
        )
    else:
        return GovernanceScore(client)
