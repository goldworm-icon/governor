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

from .governance import create_reader_by_args, create_writer_by_args


def init(sub_parser, common_parent_parser, invoke_parent_parser):
    _init_for_invoke(sub_parser, common_parent_parser, invoke_parent_parser)
    _init_for_query(sub_parser, common_parent_parser)


def _init_for_invoke(sub_parser, common_parent_parser, invoke_parent_parser):
    name = "setstep"
    desc = "setStepCost command"

    score_parser = sub_parser.add_parser(
        name,
        parents=[common_parent_parser, invoke_parent_parser],
        help=desc)

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

    score_parser.set_defaults(func=_run_set_step_cost)


def _init_for_query(sub_parser, common_parent_parser):
    name = "getstep"
    desc = "getStepCosts command"

    score_parser = sub_parser.add_parser(
        name,
        parents=[common_parent_parser],
        help=desc)

    score_parser.set_defaults(func=_run_get_step_costs)


def _run_get_step_costs(args):
    reader = create_reader_by_args(args)
    return reader.get_step_costs()


def _run_set_step_cost(args):
    step_type: str = args.step_type
    cost: int = args.cost

    writer = create_writer_by_args(args)
    return writer.set_step_cost(step_type, cost)
