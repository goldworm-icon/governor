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
import sys

from . import revision_command
from . import score_command
from . import step_command
from . import txresult_command
from .constants import DEFAULT_URL, DEFAULT_NID


def main():
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
    print(args)

    return args.func(args)


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
    parent_parser.add_argument(
        "--yes", "-y",
        action="store_true",
        required=False,
        help="Automatic yes to prompts"
    )

    return parent_parser


def create_invoke_parser() -> argparse.ArgumentParser:
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

    return parent_parser


if __name__ == "__main__":
    ret = main()
    sys.exit(ret)
