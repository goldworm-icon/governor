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

from .utils import create_governor


def init(sub_parser, parent_parser):
    name = "update"
    desc = "Install or update governance SCORE"

    score_parser = sub_parser.add_parser(name, parents=[parent_parser], help=desc)

    score_parser.add_argument(
        "score_path",
        type=str,
        nargs="?",
        help="path where governance SCORE is located\nex) ./governance"
    )

    score_parser.set_defaults(func=run)


def run(args):
    url: str = args.url
    keystore_path: str = args.keystore
    nid: int = args.nid
    password: str = args.password
    score_path: str = args.score_path

    governor = create_governor(url, nid, keystore_path, password)
    return governor.update(score_path)
