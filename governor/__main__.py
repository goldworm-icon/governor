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
import logging
import os
import sys
import time
from icon.data import TransactionResult

from . import __about__
from .command import *
from .constants import (
    DEFAULT_URL,
    DEFAULT_NID,
    PREDEFINED_ADDRESSES,
    PREDEFINED_URLS,
)
from .utils import (
    add_keystore_argument,
    add_password_argument,
    print_arguments,
    print_tx_result,
    resolve_url,
)


def main() -> int:
    commands = [
        # Query
        AccountCommand(),
        BalanceCommand(),
        BlockCommand(),
        BlockHeaderByHashCommand(),
        BondCommand(),
        BonderListCommand(),
        ConsensusInfoCommand(),
        CreateWalletCommand(),
        DataByHashCommand(),
        DelegationCommand(),
        DownloadCommand(),
        IISSInfoCommand(),
        InImportWhiteListCommand(),
        InScoreBlackListCommand(),
        IScoreCommand(),
        MainPRepsCommand(),
        MaxStepLimitCommand(),
        PRepCommand(),
        PRepsCommand(),
        PRepStatsCommand(),
        RevisionCommand(),
        ScoreApiCommand(),
        ScoreOwnerCommand(),
        ScoreStatusCommand(),
        ServiceConfigCommand(),
        StakeCommand(),
        StatusCommand(),
        StepCostsCommand(),
        StepPriceCommand(),
        SubPRepsCommand(),
        SystemRevisionCommand(),
        TermCommand(),
        TotalSupplyCommand(),
        TransactionCommand(),
        TransactionResultCommand(),
        UpdateServiceConfigCommand(),
        ValidatorsByHeightCommand(),
        VersionCommand(),
        VotesByHeightCommand(),
        WalletCommand(),

        # Invoke
        AcceptScoreCommand(),
        AddAuditorCommand(),
        AddImportWhiteListCommand(),
        AddToScoreBlackListCommand(),
        ClaimIScoreCommand(),
        DeployCommand(),
        RejectScoreCommand(),
        RemoveAuditorCommand(),
        RemoveFromScoreBlackListCommand(),
        RemoveImportWhiteListCommand(),
        SetBonderListCommand(),
        SetMaxStepLimitCommand(),
        SetRevisionCommand(),
        SetStakeCommand(),
        SetStepCostCommand(),
        SetStepPriceCommand(),
        TransferCommand(),
    ]
    commands.sort(key=lambda x: x.key)

    parser = argparse.ArgumentParser(
        prog=__about__.name,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=__about__.description,
        epilog=_get_epilog(),
    )
    sub_parser = parser.add_subparsers(title="subcommands")

    common_parent_parser = create_common_parser()
    invoke_parent_parser = create_invoke_parser()

    for command in commands:
        command.init(sub_parser, common_parent_parser, invoke_parent_parser)

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
    arguments = {}
    for name, value in vars(args).items():
        if name == "func":
            value = value.__name__
        elif name == "url":
            value = resolve_url(value)
        arguments[name] = value

    print_arguments(arguments)


def _print_result(args, result: Union[int, bytes]) -> int:
    ret = 0

    if isinstance(result, bytes):
        if len(result) == 32 and args.no_result:
            ret = _print_tx_result(args.url, result)

    return ret


def _print_tx_result(url: str, tx_hash: bytes) -> int:
    ret = 1

    if not (isinstance(tx_hash, bytes) and len(tx_hash) == 32):
        raise ValueError(f"Invalid txHash: {tx_hash}")

    # Wait to finish the requested transaction on blockchain
    time.sleep(3)

    client: icon.Client = icon.create_client(url)
    repeat = 3

    for i in range(repeat):
        try:
            tx_result: TransactionResult = client.get_transaction_result(tx_hash)
            print_tx_result(tx_result)
            break
        except:
            if i + 1 == repeat:
                print(f"Failed to get the transaction result: {tx_hash}")
            else:
                print(f"Retrying {i + 2}/{repeat} after 2 seconds...")
                time.sleep(2)

    return ret


def _get_epilog() -> str:
    urls = _get_predefined_urls()
    addresses = _get_predefined_addresses()
    envs = _get_predefined_envs()
    return f"{urls}\n\n{addresses}\n\n{envs}"


def _get_predefined_urls() -> str:
    words = ["predefined urls:"]

    for key, value in PREDEFINED_URLS.items():
        url, nid = value
        key = f"{key}({nid})"
        words.append(f"{key.rjust(12)}: {url}")

    return "\n".join(words)


def _get_predefined_addresses() -> str:
    words = ["predefined addresses:"]

    for name, address in PREDEFINED_ADDRESSES.items():
        words.append(f"{name.rjust(10)}: {address}")

    return "\n".join(words)


def _get_predefined_envs() -> str:
    envs = (
        "predefined environment variables:",
        "GOV_URL",
        "GOV_NID",
        "GOV_KEY_STORE",
        "GOV_PASSWORD",
        "GOV_STEP_LIMIT",
    )
    return "\n".join((f"{env.ljust(14)}: {os.environ.get(env, '')}" for env in envs))


def create_common_parser() -> argparse.ArgumentParser:
    default_url: str = os.environ.get("GOV_URL", DEFAULT_URL)

    parent_parser = argparse.ArgumentParser(add_help=False)
    parent_parser.add_argument(
        "--url",
        "-u",
        type=str,
        required=False,
        default=default_url,
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
    step_limit: int = int(os.environ.get("GOV_STEP_LIMIT", 0))

    parent_parser = argparse.ArgumentParser(add_help=False)
    add_password_argument(parent_parser)
    add_keystore_argument(parent_parser, required=True)
    parent_parser.add_argument(
        "--step-limit",
        "-s",
        type=int,
        required=False,
        default=step_limit,
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
    parent_parser.add_argument(
        "--estimate",
        action="store_true",
        required=False,
        default=False,
        help="estimate step to invoke a given tx",
    )

    return parent_parser


if __name__ == "__main__":
    sys.exit(main())
