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

__all__ = ("RevisionCommand", "VersionCommand", "SetRevisionCommand")

from typing import Dict

import icon
from icon.wallet import KeyWallet
from .command import Command
from ..score.governance import GovernanceScore
from ..utils import (
    get_hooks_from_args,
    print_result,
    resolve_nid,
    resolve_url,
    resolve_wallet,
)


class RevisionCommand(Command):
    def __init__(self):
        super().__init__(name="revision", readonly=True)

    def init(self, sub_parser, common_parent_parser, invoke_parent_parser):
        desc = f"getRevision command of governance score"

        score_parser = sub_parser.add_parser(
            self.name, parents=[common_parent_parser], help=desc
        )

        score_parser.set_defaults(func=self._run)

    def _run(self, args) -> int:
        hooks = get_hooks_from_args(args)
        score = _create_governance_score(args, invoke=False)
        revision: Dict[str, str] = score.get_revision(hooks=hooks)
        print_result(revision)

        return 0


class VersionCommand(Command):
    def __init__(self):
        super().__init__(name="version", readonly=True)

    def init(self, sub_parser, common_parent_parser, invoke_parent_parser):
        desc = f"getVersion command of governance score"

        score_parser = sub_parser.add_parser(
            self.name, parents=[common_parent_parser], help=desc
        )

        score_parser.set_defaults(func=self._run)

    def _run(self, args) -> int:
        hooks = get_hooks_from_args(args)
        score = _create_governance_score(args, invoke=False)
        version: str = score.get_version(hooks=hooks)
        print_result(version)

        return 0


class SetRevisionCommand(Command):
    def __init__(self):
        super().__init__(name="setRevision", readonly=False)

    def init(self, sub_parser, common_parent_parser, invoke_parent_parser):
        desc = f"{self.name} command of governance score"

        score_parser = sub_parser.add_parser(
            self.name, parents=[common_parent_parser, invoke_parent_parser], help=desc
        )

        score_parser.add_argument(
            "revision", type=int, nargs="?", default=-1, help="revision ex) 3"
        )
        score_parser.add_argument(
            "name", type=str, nargs="?", default="", help="iconservice version ex) 1.2.3"
        )

        score_parser.set_defaults(func=self._run)

    @classmethod
    def _run(cls, args) -> bytes:
        hooks = get_hooks_from_args(args, readonly=False)
        revision: int = args.revision
        name: str = args.name

        score = _create_governance_score(args, invoke=True)
        return score.set_revision(revision, name, hooks=hooks)


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
