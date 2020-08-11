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

from typing import Dict, Optional

import icon

from ..governance import create_client
from ..utils import print_response, resolve_url


def init(sub_parser, common_parent_parser, _invoke_parent_parser):
    _init_block_by_hash(sub_parser, common_parent_parser)
    _init_block_by_height(sub_parser, common_parent_parser)
    _init_last_block(sub_parser, common_parent_parser)
    _init_get_block(sub_parser, common_parent_parser)


def _init_block_by_hash(sub_parser, common_parent_parser):
    name = "blockbyhash"
    desc = "getBlockByHash command"

    score_parser = sub_parser.add_parser(
        name, parents=[common_parent_parser], help=desc
    )

    score_parser.add_argument(
        "block_hash",
        type=str,
        nargs="?",
        help="blockHash ex) 0xe2a8e2483736ba8793bebebc30673aa4fb7662763bcdc7b0d4d8a163a79c9e20",
    )

    score_parser.set_defaults(func=_get_block_by_hash)


def _init_block_by_height(sub_parser, common_parent_parser):
    name = "blockbyheight"
    desc = "getBlockByHeight command"

    score_parser = sub_parser.add_parser(
        name, parents=[common_parent_parser], help=desc
    )

    score_parser.add_argument(
        "block_height",
        type=int,
        nargs="?",
        help="blockHeight ex) 0xe2a8e2483736ba8793bebebc30673aa4fb7662763bcdc7b0d4d8a163a79c9e20",
    )

    score_parser.set_defaults(func=_get_block_by_height)


def _init_last_block(sub_parser, common_parent_parser):
    name = "lastblock"
    desc = "getLastBlock command"

    score_parser = sub_parser.add_parser(
        name, parents=[common_parent_parser], help=desc
    )

    score_parser.set_defaults(func=_get_last_block)


def _init_get_block(sub_parser, common_parent_parser):
    name = "getblock"
    desc = "icx_getBlock command"

    score_parser = sub_parser.add_parser(
        name, parents=[common_parent_parser], help=desc
    )

    score_parser.add_argument(
        "value",
        type=str,
        nargs="?",
        default=None,
        help="block_hash or block_height",
    )

    score_parser.set_defaults(func=_get_block)


def _get_block_by_hash(args) -> int:
    url: str = resolve_url(args.url)
    block_hash: bytes = icon.hex_to_bytes(args.block_hash)

    client: icon.Client = create_client(url)
    block: icon.Block = client.get_block_by_hash(block_hash)
    print_response(f"{block}")

    return 0


def _get_block_by_height(args) -> int:
    url: str = resolve_url(args.url)
    block_height: int = args.block_height

    client: icon.Client = create_client(url)
    block: icon.Block = client.get_block_by_height(block_height)
    print_response(f"{block}")

    return 0


def _get_last_block(args) -> int:
    url: str = resolve_url(args.url)

    client: icon.Client = create_client(url)
    block: icon.Block = client.get_last_block()
    print_response(f"{block}")

    return 0


def _get_block(args) -> int:
    url: str = resolve_url(args.url)
    value: Optional[str] = args.value

    if isinstance(value, str):
        if value.startswith("0x") and len(value) == 66:
            value: bytes = icon.hex_to_bytes(value)
        else:
            value: int = int(value, 0)

    client: icon.Client = create_client(url)
    result: Dict[str, str] = client.get_block(value)
    print_response(f"{result}")

    return 0
