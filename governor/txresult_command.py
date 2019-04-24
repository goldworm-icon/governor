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

from .utils import create_governor_by_args, hex_to_bytes


def init(sub_parser, parent_parser):
    name = "txresult"
    desc = "query transaction result"

    score_parser = sub_parser.add_parser(name, parents=[parent_parser], help=desc)

    score_parser.add_argument(
        "tx_hash",
        type=str,
        nargs="?",
        help="txHash ex) 0xe2a8e2483736ba8793bebebc30673aa4fb7662763bcdc7b0d4d8a163a79c9e20"
    )

    score_parser.set_defaults(func=run)


def run(args):
    tx_hash: bytes = hex_to_bytes(args.tx_hash)

    governor = create_governor_by_args(args)
    return governor.get_tx_result(tx_hash)
