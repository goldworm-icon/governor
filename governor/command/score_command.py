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

from typing import Union, Dict

from icon.data import Address

from governor.score.governance import create_writer_by_args, create_reader_by_args
from governor.utils import print_response


def init(sub_parser, common_parent_parser, invoke_parent_parser):
    _init_for_update(sub_parser, common_parent_parser, invoke_parent_parser)
    _init_for_accept_score(sub_parser, common_parent_parser, invoke_parent_parser)
    _init_for_reject_score(sub_parser, common_parent_parser, invoke_parent_parser)

    _init_for_add_auditor(sub_parser, common_parent_parser, invoke_parent_parser)
    _init_for_remove_auditor(sub_parser, common_parent_parser, invoke_parent_parser)

    _init_for_add_deployer(sub_parser, common_parent_parser, invoke_parent_parser)
    _init_for_remove_deployer(sub_parser, common_parent_parser, invoke_parent_parser)

    _init_for_add_to_score_black_list(
        sub_parser, common_parent_parser, invoke_parent_parser
    )
    _init_for_remove_from_score_black_list(
        sub_parser, common_parent_parser, invoke_parent_parser
    )

    _init_for_add_import_white_list(
        sub_parser, common_parent_parser, invoke_parent_parser
    )
    _init_for_remove_import_white_list(
        sub_parser, common_parent_parser, invoke_parent_parser
    )

    _init_for_get_score_status(sub_parser, common_parent_parser)
    _init_for_get_service_config(sub_parser, common_parent_parser)
    _init_for_update_service_config(
        sub_parser, common_parent_parser, invoke_parent_parser
    )

    _init_for_is_deployer(sub_parser, common_parent_parser)
    _init_for_is_in_score_black_list(sub_parser, common_parent_parser)
    _init_for_is_in_import_white_list(sub_parser, common_parent_parser)


def _init_for_update(sub_parser, common_parent_parser, invoke_parent_parser):
    name = "update"
    desc = "Install or update governance SCORE"

    score_parser = sub_parser.add_parser(
        name, parents=[common_parent_parser, invoke_parent_parser], help=desc
    )

    score_parser.add_argument(
        "score_path",
        type=str,
        nargs="?",
        help="path where governance SCORE is located\nex) ./governance",
    )

    score_parser.set_defaults(func=_update_governance_score)


def _update_governance_score(args) -> Union[int, str]:
    score_path: str = args.score_path
    estimate: bool = args.estimate

    writer = create_writer_by_args(args)
    ret = writer.deploy(score_path)

    if estimate:
        print_response(f"Estimate step: {ret}, {hex(ret)}")

    return ret


def _init_for_get_score_status(sub_parser, common_parent_parser):
    name = "getScoreStatus"
    desc = f"{name} command"

    score_parser = sub_parser.add_parser(
        name, parents=[common_parent_parser], help=desc
    )

    score_parser.add_argument(
        "address",
        type=str,
        nargs="?",
        help="SCORE address ex) cx8a96c0dcf0567635309809d391908c32fbca5317",
    )

    score_parser.set_defaults(func=_get_score_status)


def _get_score_status(args) -> int:
    address: Address = Address.from_string(args.address)

    reader = create_reader_by_args(args)
    result: Dict[str, str] = reader.get_score_status(address)
    print_response(result)

    return 0


def _init_for_get_service_config(sub_parser, common_parent_parser):
    name = "getServiceConfig"
    desc = f"{name} command"

    score_parser = sub_parser.add_parser(
        name, parents=[common_parent_parser], help=desc
    )

    score_parser.set_defaults(func=_get_service_config)


def _get_service_config(args) -> int:
    reader = create_reader_by_args(args)
    result: dict = reader.get_service_config()
    print_response(result)

    return 0


def _init_for_update_service_config(
    sub_parser, common_parent_parser, invoke_parent_parser
):
    name = "updateServiceConfig"
    desc = f"{name} command"

    score_parser = sub_parser.add_parser(
        name, parents=[common_parent_parser, invoke_parent_parser], help=desc
    )

    score_parser.add_argument("service_flag", type=int, nargs="?", help="")

    score_parser.set_defaults(func=_update_service_config)


def _update_service_config(args):
    service_flag: int = args.service_flag

    writer = create_writer_by_args(args)
    return writer.update_service_config(service_flag)


def _init_for_accept_score(sub_parser, common_parent_parser, invoke_parent_parser):
    name = "acceptScore"
    desc = f"{name} command"

    score_parser = sub_parser.add_parser(
        name, parents=[common_parent_parser, invoke_parent_parser], help=desc
    )

    score_parser.add_argument(
        "tx_hash",
        type=str,
        nargs="?",
        help="txHash ex) 0xe2a8e2483736ba8793bebebc30673aa4fb7662763bcdc7b0d4d8a163a79c9e20",
    )

    score_parser.set_defaults(func=_accept_score)


def _accept_score(args) -> bytes:
    tx_hash: str = args.tx_hash

    writer = create_writer_by_args(args)
    return writer.accept_score(tx_hash)


def _init_for_reject_score(sub_parser, common_parent_parser, invoke_parent_parser):
    name = "rejectScore"
    desc = f"{name} command"

    score_parser = sub_parser.add_parser(
        name, parents=[common_parent_parser, invoke_parent_parser], help=desc
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

    score_parser.set_defaults(func=_reject_score)


def _reject_score(args) -> bytes:
    tx_hash: str = args.tx_hash
    reason: str = args.reason

    writer = create_writer_by_args(args)
    return writer.reject_score(tx_hash, reason)


def _init_for_add_auditor(sub_parser, common_parent_parser, invoke_parent_parser):
    name = "addAuditor"
    desc = f"{name} command"

    score_parser = sub_parser.add_parser(
        name, parents=[common_parent_parser, invoke_parent_parser], help=desc
    )

    score_parser.add_argument("address", type=str, nargs="?", help="")

    score_parser.set_defaults(func=_add_auditor)


def _add_auditor(args) -> bytes:
    address: str = args.address

    writer = create_writer_by_args(args)
    return writer.add_auditor(address)


def _init_for_remove_auditor(sub_parser, common_parent_parser, invoke_parent_parser):
    name = "removeAuditor"
    desc = f"{name} command"

    score_parser = sub_parser.add_parser(
        name, parents=[common_parent_parser, invoke_parent_parser], help=desc
    )

    score_parser.add_argument("address", type=str, nargs="?", help="")

    score_parser.set_defaults(func=_remove_auditor)


def _remove_auditor(args) -> bytes:
    address: str = args.address

    writer = create_writer_by_args(args)
    return writer.remove_auditor(address)


def _init_for_add_deployer(sub_parser, common_parent_parser, invoke_parent_parser):
    name = "addDeployer"
    desc = f"{name} command"

    score_parser = sub_parser.add_parser(
        name, parents=[common_parent_parser, invoke_parent_parser], help=desc
    )

    score_parser.add_argument("address", type=str, nargs="?", help="")

    score_parser.set_defaults(func=_add_deployer)


def _add_deployer(args) -> bytes:
    address: str = args.address

    writer = create_writer_by_args(args)
    return writer.add_deployer(address)


def _init_for_remove_deployer(sub_parser, common_parent_parser, invoke_parent_parser):
    name = "removeDeployer"
    desc = f"{name} command"

    score_parser = sub_parser.add_parser(
        name, parents=[common_parent_parser, invoke_parent_parser], help=desc
    )

    score_parser.add_argument("address", type=str, nargs="?", help="")

    score_parser.set_defaults(func=_remove_deployer)


def _remove_deployer(args) -> bytes:
    address: str = args.address

    writer = create_writer_by_args(args)
    return writer.remove_deployer(address)


def _init_for_add_to_score_black_list(
    sub_parser, common_parent_parser, invoke_parent_parser
):
    name = "addToScoreBlackList"
    desc = f"{name} command"

    score_parser = sub_parser.add_parser(
        name, parents=[common_parent_parser, invoke_parent_parser], help=desc
    )

    score_parser.add_argument("address", type=str, nargs="?", help="")

    score_parser.set_defaults(func=_add_to_score_black_list)


def _add_to_score_black_list(args) -> bytes:
    address: str = args.address

    writer = create_writer_by_args(args)
    return writer.add_to_score_black_list(address)


def _init_for_remove_from_score_black_list(
    sub_parser, common_parent_parser, invoke_parent_parser
):
    name = "removeFromScoreBlackList"
    desc = f"{name} command"

    score_parser = sub_parser.add_parser(
        name, parents=[common_parent_parser, invoke_parent_parser], help=desc
    )

    score_parser.add_argument("address", type=str, nargs="?", help="")

    score_parser.set_defaults(func=_remove_from_score_black_list)


def _remove_from_score_black_list(args) -> bytes:
    address: str = args.address

    writer = create_writer_by_args(args)
    return writer.remove_from_score_black_list(address)


def _init_for_add_import_white_list(
    sub_parser, common_parent_parser, invoke_parent_parser
):
    name = "addImportWhiteList"
    desc = f"{name} command"

    score_parser = sub_parser.add_parser(
        name, parents=[common_parent_parser, invoke_parent_parser], help=desc
    )

    score_parser.add_argument("import_stmt", type=str, nargs="?", help="")

    score_parser.set_defaults(func=_add_import_white_list)


def _add_import_white_list(args) -> bytes:
    import_stmt: str = args.import_stmt

    writer = create_writer_by_args(args)
    return writer.add_import_white_list(import_stmt)


def _init_for_remove_import_white_list(
    sub_parser, common_parent_parser, invoke_parent_parser
):
    name = "removeImportWhiteList"
    desc = f"{name} command"

    score_parser = sub_parser.add_parser(
        name, parents=[common_parent_parser, invoke_parent_parser], help=desc
    )

    score_parser.add_argument("import_stmt", type=str, nargs="?", help="")

    score_parser.set_defaults(func=_remove_import_white_list)


def _remove_import_white_list(args) -> bytes:
    import_stmt: str = args.import_stmt

    writer = create_writer_by_args(args)
    return writer.remove_import_white_list(import_stmt)


def _init_for_is_deployer(sub_parser, common_parent_parser):
    name = "isDeployer"
    desc = f"{name} command"

    score_parser = sub_parser.add_parser(
        name, parents=[common_parent_parser], help=desc
    )

    score_parser.add_argument("address", type=str, nargs="?", help="")

    score_parser.set_defaults(func=_is_deployer)


def _is_deployer(args) -> int:
    address: str = args.address

    reader = create_reader_by_args(args)
    is_deployer: bool = reader.is_deployer(address)
    print_response(f"is_deployer: {is_deployer}")

    return 0


def _init_for_is_in_score_black_list(sub_parser, common_parent_parser):
    name = "isInScoreBlackList"
    desc = f"{name} command"

    score_parser = sub_parser.add_parser(
        name, parents=[common_parent_parser], help=desc
    )

    score_parser.add_argument("address", type=str, nargs="?", help="")

    score_parser.set_defaults(func=_is_in_score_black_list)


def _is_in_score_black_list(args) -> int:
    address: str = args.address

    reader = create_reader_by_args(args)
    is_in_score_black_list: bool = reader.is_in_score_black_list(address)
    print_response(f"is_in_score_black_list: {is_in_score_black_list}")

    return 0


def _init_for_is_in_import_white_list(sub_parser, common_parent_parser):
    name = "isInImportWhiteList"
    desc = f"{name} command"

    # todo: governor 입력시 isImportWhiteList 줄바꿈 현상 확인
    score_parser = sub_parser.add_parser(
        name, parents=[common_parent_parser], help=desc
    )

    score_parser.add_argument("import_stmt", type=str, nargs="?", help="")

    score_parser.set_defaults(func=_is_in_import_white_list)


def _is_in_import_white_list(args) -> int:
    import_stmt: str = args.import_stmt

    reader = create_reader_by_args(args)
    is_in_import_white_list: bool = reader.is_in_import_white_list(import_stmt)
    print_response(f"is_in_import_white_list: {is_in_import_white_list}")

    return 0
