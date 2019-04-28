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

from .governance import create_writer_by_args, create_reader_by_args


def init(sub_parser, common_parent_parser, invoke_parent_parser):
    _init_for_update(sub_parser, common_parent_parser, invoke_parent_parser)
    _init_for_score_status(sub_parser, common_parent_parser)


def _init_for_update(sub_parser, common_parent_parser, invoke_parent_parser):
    name = "update"
    desc = "Install or update governance SCORE"

    score_parser = sub_parser.add_parser(
        name,
        parents=[common_parent_parser, invoke_parent_parser],
        help=desc)

    score_parser.add_argument(
        "score_path",
        type=str,
        nargs="?",
        help="path where governance SCORE is located\nex) ./governance"
    )

    score_parser.set_defaults(func=_update_governance_score)


def _update_governance_score(args):
    score_path: str = args.score_path

    writer = create_writer_by_args(args)
    return writer.update(score_path)


def _init_for_score_status(sub_parser, common_parent_parser):
    name = "getscorestatus"
    desc = "getScoreStatus command"

    score_parser = sub_parser.add_parser(
        name,
        parents=[common_parent_parser],
        help=desc)

    score_parser.add_argument(
        "address",
        type=str,
        nargs="?",
        help="SCORE address ex) cx8a96c0dcf0567635309809d391908c32fbca5317"
    )

    score_parser.set_defaults(func=_get_score_status)


def _get_score_status(args) -> dict:
    address: str = args.address

    reader = create_reader_by_args(args)
    return reader.get_score_status(address)
