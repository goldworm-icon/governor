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

from . import score_command


def main():
    handlers = {
        score_command.init
    }

    parser = argparse.ArgumentParser(prog="governor", description="Governor SCORE controller")
    sub_parser = parser.add_subparsers(title="subcommands")
    parent_parser = create_parent_parser()

    for handler in handlers:
        handler(sub_parser, parent_parser)

    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        return 1

    args = parser.parse_args()
    print(args)

    return args.func(args)


def create_parent_parser() -> argparse.ArgumentParser:
    parent_parser = argparse.ArgumentParser(add_help=False)
    parent_parser.add_argument(
        "--url", "-u",
        type=str,
        required=True,
        default="http://localhost:9000/api/v3",
        help="node url"
    )
    parent_parser.add_argument(
        "--nid",
        type=int,
        required=True,
        default=3,
        help="networkId ex) mainnet(1), testnet(2)"
    )
    parent_parser.add_argument(
        "--keystore", "-k",
        type=str,
        required=True,
        help="keystore file path"
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


if __name__ == "__main__":
    ret = main()
    sys.exit(ret)
