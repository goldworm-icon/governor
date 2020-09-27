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

import functools
from typing import Dict, Union

import icon
from icon.wallet import KeyWallet

from .command import Command
from ..score.governance import GovernanceScore
from ..utils import (
    confirm_transaction,
    print_request,
    print_response,
    resolve_nid,
    resolve_url,
    resolve_wallet,
)


class StepCostsCommand(Command):
    def __init__(self):
        super().__init__(name="stepCosts", readonly=True)

    def init(self, sub_parser, common_parent_parser, invoke_parent_parser):
        desc = f"getStepCosts command of governance score"

        score_parser = sub_parser.add_parser(
            self.name, parents=[common_parent_parser], help=desc
        )

        score_parser.set_defaults(func=self._run)

    def _run(self, args):
        hooks = {"request": print_request, "response": print_response}
        score = _create_governance_score(args, invoke=not self.readonly)

        result: Dict[str, str] = score.get_step_costs(hooks=hooks)
        step_costs: Dict[str, int] = _convert_hex_to_int(result)
        print_response(step_costs)

        return 0


class StepPriceCommand(Command):
    def __init__(self):
        super().__init__(name="stepPrice", readonly=True)

    def init(self, sub_parser, common_parent_parser, invoke_parent_parser):
        desc = f"getStepPrice command of governance score"

        score_parser = sub_parser.add_parser(
            self.name, parents=[common_parent_parser], help=desc
        )

        score_parser.set_defaults(func=self._run)

    def _run(self, args) -> int:
        hooks = {"request": print_request, "response": print_response}
        score = _create_governance_score(args, invoke=not self.readonly)

        step_price: int = score.get_step_price(hooks=hooks)
        print_response(f"stepPrice: {step_price:_}, {hex(step_price)}")

        return 0


class MaxStepLimitCommand(Command):
    def __init__(self):
        super().__init__(name="maxStepLimit", readonly=True)

    def init(self, sub_parser, common_parent_parser, invoke_parent_parser):
        desc = f"getMaxStepLimit command"

        score_parser = sub_parser.add_parser(
            self.name, parents=[common_parent_parser], help=desc
        )
        score_parser.add_argument("context_type", type=str, nargs="?", help="")
        score_parser.set_defaults(func=self._run)

    def _run(self, args) -> int:
        # "invoke" or "query"
        context_type: str = args.context_type
        score = _create_governance_score(args, invoke=not self.readonly)
        max_step_limit: int = score.get_max_step_limit(context_type)
        print_response(f"maxStepLimit: {max_step_limit}")

        return 0


class SetStepCostCommand(Command):
    def __init__(self):
        super().__init__(name="setStepCost", readonly=False)

    def init(self, sub_parser, common_parent_parser, invoke_parent_parser):
        desc = f"setStepCost command of governance score"

        score_parser = sub_parser.add_parser(
            self.name,
            parents=[common_parent_parser, invoke_parent_parser],
            help=desc
        )

        score_parser.add_argument(
            "step_type",
            type=str,
            nargs="?",
            help="step_type ex) default, apiCall, contractSet, input, eventlog",
        )
        score_parser.add_argument(
            "cost", type=int, nargs="?", default=-1, help="cost ex) 1000"
        )

        score_parser.set_defaults(func=self._run)

    def _run(self, args) -> Union[bytes, int]:
        hooks = {
            "request": functools.partial(confirm_transaction, yes=args.yes),
            "response": print_response
        }
        step_type: str = args.step_type
        cost: int = args.cost

        score = _create_governance_score(args, invoke=not self.readonly)
        return score.set_step_cost(step_type, cost, hooks=hooks)


class SetStepPriceCommand(Command):
    def __init__(self):
        super().__init__(name="setStepPrice", readonly=False)

    def init(self, sub_parser, common_parent_parser, invoke_parent_parser):
        desc = f"{self.name} command of governance score"

        score_parser = sub_parser.add_parser(
            self.name, parents=[common_parent_parser, invoke_parent_parser], help=desc
        )

        score_parser.add_argument("step_price", type=int, nargs="?", help="")

        score_parser.set_defaults(func=self._run)

    def _run(self, args) -> Union[bytes, int]:
        hooks = {
            "request": functools.partial(confirm_transaction, yes=args.yes),
            "response": print_response
        }

        step_price: int = args.step_price
        score = _create_governance_score(args, invoke=not self.readonly)
        return score.set_step_price(step_price, hooks=hooks)


class SetMaxStepLimitCommand(Command):
    def __init__(self):
        super().__init__(name="setMaxStepLimit", readonly=False)

    def init(self, sub_parser, common_parent_parser, invoke_parent_parser):
        desc = f"{self.name} command of governance score"

        score_parser = sub_parser.add_parser(
            self.name,
            parents=[common_parent_parser, invoke_parent_parser],
            help=desc
        )

        score_parser.add_argument("context_type", type=str, nargs="?", help="")
        score_parser.add_argument("value", type=int, nargs="?", default=-1, help="")

        score_parser.set_defaults(func=self._run)

    def _run(self, args) -> Union[bytes, int]:
        hooks = {
            "request": functools.partial(confirm_transaction, yes=args.yes),
            "response": print_response
        }

        context_type: str = args.context_type
        value: int = args.value

        score = _create_governance_score(args, invoke=not self.readonly)
        return score.set_max_step_limit(context_type, value, hooks=hooks)


def _convert_hex_to_int(step_costs: Dict[str, str]) -> Dict[str, int]:
    ret = {}

    for key in step_costs:
        value: str = step_costs[key]
        assert isinstance(value, str)

        ret[key] = int(value, base=0)

    return ret


def _create_governance_score(args, invoke: bool) -> GovernanceScore:
    url: str = resolve_url(args.url)
    nid: int = resolve_nid(args.nid, args.url)

    client: icon.Client = icon.create_client(url)

    if invoke:
        step_limit: int = args.step_limit
        estimate: bool = args.estimate
        wallet: KeyWallet = resolve_wallet(args)

        return GovernanceScore(
            client=client,
            owner=wallet,
            nid=nid,
            step_limit=step_limit,
            estimate=estimate
        )
    else:
        return GovernanceScore(client)
