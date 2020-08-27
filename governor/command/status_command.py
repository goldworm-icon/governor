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

from typing import Dict

import icon

from governor.score.governance import create_client
from ..utils import print_response, resolve_url


def init(sub_parser, common_parent_parser, _invoke_parent_parser):
    _init_get_status(sub_parser, common_parent_parser)


def _init_get_status(sub_parser, common_parent_parser):
    name = "getStatus"
    desc = "ise_getStatus command"

    score_parser = sub_parser.add_parser(
        name, parents=[common_parent_parser], help=desc
    )

    score_parser.add_argument(
        "filter", type=str, nargs="?", help="filter ex) lastblock"
    )

    score_parser.set_defaults(func=_get_status)


def _get_status(args) -> int:
    url: str = resolve_url(args.url)
    _filter: str = args.filter

    client: icon.Client = create_client(url)
    result: Dict[str, str] = client.get_status()
    print_response(f"{result}")

    return 0
