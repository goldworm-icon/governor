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

import icon
from icon.data import Transaction, TransactionResult
from icon.data import hex_to_bytes

from ..utils import (
    create_client,
    print_response,
    resolve_url,
)


def init(sub_parser, common_parent_parser, _invoke_parent_parser):
    _init_tx(sub_parser, common_parent_parser)
    _init_tx_result(sub_parser, common_parent_parser)


def _init_tx(sub_parser, common_parent_parser):
    name = "tx"
    desc = "getTransaction command"

    score_parser = sub_parser.add_parser(
        name, parents=[common_parent_parser], help=desc
    )

    score_parser.add_argument(
        "tx_hash",
        type=str,
        nargs="?",
        help="txHash ex) 0xe2a8e2483736ba8793bebebc30673aa4fb7662763bcdc7b0d4d8a163a79c9e20",
    )

    score_parser.set_defaults(func=_get_tx)


def _init_tx_result(sub_parser, common_parent_parser):
    name = "txresult"
    desc = "getTransactionResult command"

    score_parser = sub_parser.add_parser(
        name, parents=[common_parent_parser], help=desc
    )

    score_parser.add_argument(
        "tx_hash",
        type=str,
        nargs="?",
        help="txHash ex) 0xe2a8e2483736ba8793bebebc30673aa4fb7662763bcdc7b0d4d8a163a79c9e20",
    )

    score_parser.set_defaults(func=_get_tx_result)


def _get_tx(args) -> int:
    url: str = resolve_url(args.url)
    tx_hash: bytes = hex_to_bytes(args.tx_hash)

    client: icon.Client = create_client(url)
    tx: Transaction = client.get_transaction(tx_hash)
    print_response(str(tx))

    return 0


def _get_tx_result(args) -> int:
    url: str = resolve_url(args.url)
    tx_hash: bytes = hex_to_bytes(args.tx_hash)

    client: icon.Client = create_client(url)
    tx_result: TransactionResult = client.get_transaction_result(tx_hash)
    print_response(f"{tx_result}")

    return 0
