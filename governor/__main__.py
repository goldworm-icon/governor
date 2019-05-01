# -*- coding: utf-8 -*-

# Copyright 2019 ICON Foundation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import argparse
import pprint
import sys
import time
from typing import Optional

from . import revision_command
from . import score_command
from . import step_command
from . import txresult_command
from .constants import DEFAULT_URL, DEFAULT_NID
from .governance import create_icon_service


def main() -> int:
    handlers = [
        score_command.init,
        step_command.init,
        revision_command.init,
        txresult_command.init
    ]

    parser = argparse.ArgumentParser(
        prog="governor", description="Governor SCORE controller")
    sub_parser = parser.add_subparsers(title="subcommands")

    common_parent_parser = create_common_parser()
    invoke_parent_parser = create_invoke_parser()

    for handler in handlers:
        handler(sub_parser, common_parent_parser, invoke_parent_parser)

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        return 1

    args = parser.parse_args()
    _print_arguments(args)

    ret = _prompt_continue(args)
    if ret == 0:
        ret: Optional[int, str] = args.func(args)
        if isinstance(ret, str):
            if not args.no_result:
                ret = _print_tx_result(args, tx_hash=ret)
            else:
                print(f"txresult: {ret}")
                ret = 0

        return ret


def _print_arguments(args):
    print("Arguments ======================")

    for name, value in args._get_kwargs():
        print(f"* {name}: {value}")

    print("================================")


def _prompt_continue(args) -> int:
    if hasattr(args, "yes") and not args.yes:
        ret = input("Continue? [Y/n]")
        if ret in ("n", "N"):
            return 1

    return 0


def _print_tx_result(args, tx_hash: str) -> int:
    if tx_hash.startswith("0x") and len(tx_hash) == 66:
        time.sleep(2)
        icon_service = create_icon_service(args.url)
        tx_result: dict = icon_service.get_transaction_result(tx_hash)
        pprint.pprint(tx_result)
        ret = tx_result["status"]
    else:
        # tx_hash is not tx hash format
        print(tx_hash)
        ret = 1

    return ret


def create_common_parser() -> argparse.ArgumentParser:
    parent_parser = argparse.ArgumentParser(add_help=False)
    parent_parser.add_argument(
        "--url", "-u",
        type=str,
        required=False,
        default=DEFAULT_URL,
        help=f"node url default) {DEFAULT_URL}"
    )
    parent_parser.add_argument(
        "--nid", "-n",
        type=int,
        required=False,
        default=DEFAULT_NID,
        help=f"networkId default({DEFAULT_NID} ex) mainnet(1), testnet(2)"
    )
    parent_parser.add_argument(
        "--verbose", "-v",
        required=False,
        action="store_true"
    )

    return parent_parser


def create_invoke_parser() -> argparse.ArgumentParser:
    """Common options for invoke commands

    :return:
    """

    parent_parser = argparse.ArgumentParser(add_help=False)

    parent_parser.add_argument(
        "--password", "-p",
        type=str,
        required=False,
        default=None,
        help="keystore password"
    )
    parent_parser.add_argument(
        "--keystore", "-k",
        type=str,
        required=True,
        help="keystore file path"
    )
    parent_parser.add_argument(
        "--no-result",
        action="store_true",
        required=False,
        help="Display transaction result automatically for invoke commands"
    )
    parent_parser.add_argument(
        "--yes", "-y",
        action="store_true",
        required=False,
        help="Automatic yes to prompts"
    )

    return parent_parser


if __name__ == "__main__":
    sys.exit(main())
