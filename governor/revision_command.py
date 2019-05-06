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
from .utils import print_response


def init(sub_parser, common_parent_parser, invoke_parent_parser):
    _init_for_set_revision(sub_parser, common_parent_parser, invoke_parent_parser)
    _init_for_get_revision(sub_parser, common_parent_parser)


def _init_for_set_revision(sub_parser, common_parent_parser, invoke_parent_parser):
    name = "setRevision"
    desc = f"{name} command"

    score_parser = sub_parser.add_parser(
        name,
        parents=[common_parent_parser, invoke_parent_parser],
        help=desc)

    score_parser.add_argument(
        "revision",
        type=int,
        nargs="?",
        default=-1,
        help="revision ex) 3"
    )
    score_parser.add_argument(
        "name",
        type=str,
        nargs="?",
        default="",
        help="iconservice version ex) 1.2.3"
    )

    score_parser.set_defaults(func=_set_revision)


def _set_revision(args) -> str:
    revision: int = args.revision
    name: str = args.name

    writer = create_writer_by_args(args)
    return writer.set_revision(revision, name)


def _init_for_get_revision(sub_parser, common_parent_parser):
    name = "getRevision"
    desc = f"{name} command"

    score_parser = sub_parser.add_parser(
        name,
        parents=[common_parent_parser],
        help=desc)

    score_parser.set_defaults(func=_get_revision)


def _get_revision(args) -> int:
    reader = create_reader_by_args(args)
    revision: dict = reader.get_revision()

    print_response(revision)

    return 0

