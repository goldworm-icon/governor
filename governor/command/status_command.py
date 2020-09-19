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

from typing import Dict, Any

import icon
from icon.data.utils import str_to_object_by_type

from .command import Command
from .. import result_type
from ..utils import (
    print_request,
    print_response,
    print_result,
    resolve_url,
)


class StatusCommand(Command):
    def __init__(self):
        self._name = "status"
        self._hooks = {"request": print_request, "response": print_response}

    @property
    def name(self) -> str:
        return self._name

    def init(self, sub_parser, common_parent_parser, invoke_parent_parser):
        desc = "ise_getStatus command"

        score_parser = sub_parser.add_parser(
            self._name, parents=[common_parent_parser], help=desc
        )

        score_parser.add_argument(
            "filter", type=str, nargs="?", help="filter ex) lastblock"
        )

        score_parser.set_defaults(func=self._run)

    def _run(self, args) -> int:
        url: str = resolve_url(args.url)
        _filter: str = args.filter

        client: icon.Client = icon.create_client(url)
        result: Dict[str, str] = client.get_status(hooks=self._hooks)
        result: Dict[str, Any] = str_to_object_by_type(result_type.STATUS, result)
        print_result(result)

        return 0
