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

from .utils import create_governor_by_args


def init(sub_parser, parent_parser):
    name = "rev"
    desc = "revision command"

    score_parser = sub_parser.add_parser(name, parents=[parent_parser], help=desc)

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

    score_parser.set_defaults(func=run)


def run(args):
    revision: int = args.revision
    name: str = args.name

    governor = create_governor_by_args(args)

    if revision < 0:
        return governor.get_revision()
    else:
        return governor.set_revision(revision, name)
