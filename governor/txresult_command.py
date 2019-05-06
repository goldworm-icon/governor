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

from .governance import create_reader_by_args
from .utils import print_tx_result


def init(sub_parser, common_parent_parser, invoke_parent_parser):
    name = "txresult"
    desc = "getTransactionResult command"

    score_parser = sub_parser.add_parser(
        name,
        parents=[common_parent_parser],
        help=desc)

    score_parser.add_argument(
        "tx_hash",
        type=str,
        nargs="?",
        help="txHash ex) 0xe2a8e2483736ba8793bebebc30673aa4fb7662763bcdc7b0d4d8a163a79c9e20"
    )

    score_parser.set_defaults(func=_get_tx_result)


def _get_tx_result(args) -> int:
    tx_hash: str = args.tx_hash

    reader = create_reader_by_args(args)
    tx_result: dict = reader.get_tx_result(tx_hash)
    print_tx_result(tx_result)

    return 0
