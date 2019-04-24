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
    name = "step"
    desc = "step command"

    score_parser = sub_parser.add_parser(name, parents=[parent_parser], help=desc)

    score_parser.add_argument(
        "step_type",
        type=str,
        nargs="?",
        help="step_type ex) default, apiCall, contractSet, input, eventlog"
    )
    score_parser.add_argument(
        "cost",
        type=int,
        nargs="?",
        default=-1,
        help="cost ex) 1000"
    )

    score_parser.set_defaults(func=run)


def run(args):
    step_type: str = args.step_type
    cost: int = args.cost

    governor = create_governor_by_args(args)

    if step_type is None:
        return governor.get_step_costs()
    else:
        return governor.set_step_cost(step_type, cost)
