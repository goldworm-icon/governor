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
import json
import logging
import sys
import time
from typing import Union

import icon

from . import __about__
from .command import (
    step_command,
    revision_command,
    score_command,
    transaction_command,
    block_command,
    status_command,
)
from .constants import (
    DEFAULT_URL,
    DEFAULT_NID,
    COLUMN,
    PREDEFINED_URLS,
)
from .governance import create_client
from .utils import (
    print_title,
    resolve_url,
)


def main() -> int:
    handlers = (
        score_command.init,
        step_command.init,
        revision_command.init,
        transaction_command.init,
        block_command.init,
        status_command.init,
    )

    parser = argparse.ArgumentParser(
        prog=__about__.name,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=__about__.description,
        epilog=_get_epilog(),
    )
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

    _init_logger(args)

    result: Union[int, bytes] = args.func(args)
    ret: int = _print_result(args, result)
    return ret


def _init_logger(args):
    if not hasattr(args, "log"):
        return

    log_level = {
        "debug": logging.DEBUG,
        "info": logging.INFO,
        "warn": logging.WARN,
        "warning": logging.WARNING,
        "error": logging.ERROR,
        "fatal": logging.FATAL,
        "critical": logging.CRITICAL,
    }

    logging.basicConfig(
        filename="governor.log", level=log_level.get(args.log, logging.DEBUG)
    )


def _print_arguments(args):
    print_title("Arguments", COLUMN)

    arguments = {}
    for name, value in args._get_kwargs():
        if name == "func":
            value = value.__name__
        elif name == "url":
            value = resolve_url(value)
        arguments[name] = value

    print(f"{json.dumps(arguments, indent=4)}\n")


def _print_result(args, result: Union[int, bytes]) -> int:
    ret = 0

    if isinstance(result, bytes) and not args.no_result:
        ret = _print_tx_result(args.url, result)

    return ret


def _print_tx_result(url: str, tx_hash: bytes) -> int:
    ret = 1

    if not (isinstance(tx_hash, bytes) and len(tx_hash) == 32):
        raise ValueError(f"Invalid txHash: {tx_hash}")

    # Wait to finish the requested transaction on blockchain
    time.sleep(3)

    client: icon.Client = create_client(url)
    repeat = 3

    for i in range(repeat):
        try:
            tx_result: icon.TransactionResult = client.get_transaction_result(tx_hash)
            print(tx_result)
            break
        except:
            if i + 1 == repeat:
                print(f"Failed to get the transaction result: {tx_hash}")
            else:
                print(f"Retrying {i + 2}/{repeat} after 2 seconds...")
                time.sleep(2)

    return ret


def _get_epilog() -> str:
    words = ["predefined urls:"]

    for key, value in PREDEFINED_URLS.items():
        url, nid = value
        key = f"{key}({nid})"
        words.append(f"{key:15s}: {url}")

    return "\n".join(words)


def create_common_parser() -> argparse.ArgumentParser:
    parent_parser = argparse.ArgumentParser(add_help=False)
    parent_parser.add_argument(
        "--url",
        "-u",
        type=str,
        required=False,
        default=DEFAULT_URL,
        help=f"node url default) {DEFAULT_URL}",
    )
    parent_parser.add_argument(
        "--nid",
        "-n",
        type=int,
        required=False,
        default=-1,
        help=f"networkId default({DEFAULT_NID} ex) mainnet(1), testnet(2)",
    )
    parent_parser.add_argument("--verbose", "-v", required=False, action="store_true")
    parent_parser.add_argument(
        "--log",
        type=str,
        required=False,
        help=(
            "Write logging messages to 'governor.log' with a given level\n"
            "ex) debug, info, warn, error, fatal"
        ),
    )

    return parent_parser


def create_invoke_parser() -> argparse.ArgumentParser:
    """Common options for invoke commands

    :return:
    """

    parent_parser = argparse.ArgumentParser(add_help=False)

    parent_parser.add_argument(
        "--password",
        "-p",
        type=str,
        required=False,
        default=None,
        help="keystore password",
    )
    parent_parser.add_argument(
        "--keystore", "-k", type=str, required=True, help="keystore file path"
    )
    parent_parser.add_argument(
        "--step-limit",
        "-s",
        type=int,
        required=False,
        default=0,
        help="stepLimit configuration",
    )
    parent_parser.add_argument(
        "--no-result",
        action="store_true",
        required=False,
        help="Display transaction result automatically after invoking is done",
    )
    parent_parser.add_argument(
        "--yes",
        "-y",
        action="store_true",
        required=False,
        help="Automatic yes to prompts",
    )

    return parent_parser


if __name__ == "__main__":
    sys.exit(main())
