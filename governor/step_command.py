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
from typing import Optional

from .governance import create_reader_by_args, create_writer_by_args
from .utils import print_response


def init(sub_parser, common_parent_parser, invoke_parent_parser):
    _init_for_set_step_cost(sub_parser, common_parent_parser, invoke_parent_parser)
    _init_for_set_step_price(sub_parser, common_parent_parser, invoke_parent_parser)
    _init_for_set_max_step_limit(sub_parser, common_parent_parser, invoke_parent_parser)
    _init_for_get_step_costs(sub_parser, common_parent_parser)
    _init_for_get_step_price(sub_parser, common_parent_parser)
    _init_for_get_max_step_limit(sub_parser, common_parent_parser)


def _init_for_set_step_cost(sub_parser, common_parent_parser, invoke_parent_parser):
    name = "setStepCost"
    desc = f"{name} command"

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

    score_parser.set_defaults(func=_set_step_cost)


def _set_step_cost(args) -> str:
    step_type: str = args.step_type
    cost: int = args.cost

    writer = create_writer_by_args(args)
    tx_result: Optional[str] = writer.set_step_cost(step_type, cost)

    return tx_result


def _init_for_set_step_price(sub_parser, common_parent_parser, invoke_parent_parser):
    name = "setStepPrice"
    desc = f"{name} command"

    score_parser = sub_parser.add_parser(
        name,
        parents=[common_parent_parser, invoke_parent_parser],
        help=desc)

    score_parser.add_argument(
        "step_price",
        type=int,
        nargs="?",
        help=""
    )

    score_parser.set_defaults(func=_set_step_price)


def _set_step_price(args) -> str:
    step_price: int = args.step_price

    writer = create_writer_by_args(args)
    tx_result: Optional[str] = writer.set_step_price(step_price)

    return tx_result


def _init_for_set_max_step_limit(sub_parser, common_parent_parser, invoke_parent_parser):
    name = "setMaxStepLimit"
    desc = f"{name} command"

    score_parser = sub_parser.add_parser(
        name,
        parents=[common_parent_parser, invoke_parent_parser],
        help=desc)

    score_parser.add_argument(
        "context_type",
        type=str,
        nargs="?",
        help=""
    )
    score_parser.add_argument(
        "value",
        type=int,
        nargs="?",
        default=-1,
        help=""
    )

    score_parser.set_defaults(func=_set_max_step_limit)


def _set_max_step_limit(args) -> str:
    context_type: str = args.context_type
    value: int = args.value

    writer = create_writer_by_args(args)
    tx_result: Optional[str] = writer.set_max_step_limit(context_type, value)

    return tx_result


def _init_for_get_step_costs(sub_parser, common_parent_parser):
    name = "getStepCosts"
    desc = f"{name} command"

    score_parser = sub_parser.add_parser(
        name,
        parents=[common_parent_parser],
        help=desc)

    score_parser.set_defaults(func=_get_step_costs)


def _get_step_costs(args) -> int:
    reader = create_reader_by_args(args)
    step_costs: dict = reader.get_step_costs()
    step_costs = _convert_hex_to_int(step_costs)

    print_response(step_costs)

    return 0


def _convert_hex_to_int(step_costs: dict) -> dict:
    for key in step_costs:
        value: str = step_costs[key]
        assert isinstance(value, str)

        step_costs[key] = int(value, 16)

    return step_costs


def _init_for_get_step_price(sub_parser, common_parent_parser):
    name = "getStepPrice"
    desc = f"{name} command"

    score_parser = sub_parser.add_parser(
        name,
        parents=[common_parent_parser],
        help=desc)

    score_parser.set_defaults(func=_get_step_price)


def _get_step_price(args) -> int:
    reader = create_reader_by_args(args)
    step_price: str = reader.get_step_price()

    print_response(f"stepPrice: {int(step_price, 16)}")

    return 0


def _init_for_get_max_step_limit(sub_parser, common_parent_parser):
    name = "getMaxStepLimit"
    desc = f"{name} command"

    score_parser = sub_parser.add_parser(
        name,
        parents=[common_parent_parser],
        help=desc)

    score_parser.add_argument(
        "context_type",
        type=str,
        nargs="?",
        help=""
    )

    score_parser.set_defaults(func=_get_max_step_limit)


def _get_max_step_limit(args) -> int:
    context_type: str = args.context_type

    reader = create_reader_by_args(args)
    max_step_limit: dict = reader.get_max_step_limit(context_type)
    max_step_limit = int(max_step_limit, 16)

    # print_response(f"MaxStepLimit : {int(max_step_limit, 16)}")
    print_response(max_step_limit)

    return 0
