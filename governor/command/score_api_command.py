# -*- coding: utf-8 -*-

from typing import Dict

import icon
from icon.data import (
    Address,
)

from .command import Command
from ..utils import (
    get_address_from_args,
    print_request,
    print_response,
    print_result,
    resolve_address,
    resolve_url,
)


class ScoreApiCommand(Command):
    def __init__(self):
        super().__init__(name="scoreApi", readonly=True)

    def init(self, sub_parser, common_parent_parser, invoke_parent_parser):
        desc = f"icx_getScoreApi command"

        score_parser = sub_parser.add_parser(
            self.name, parents=[common_parent_parser], help=desc
        )

        score_parser.add_argument(
            "address",
            type=str,
            help="Contract address to query"
        )

        score_parser.set_defaults(func=self._run)

    @classmethod
    def _run(cls, args) -> int:
        hooks = {"request": print_request, "response": print_response}

        address: Address = get_address_from_args(args)
        url: str = resolve_url(args.url)

        client: icon.Client = icon.create_client(url)
        result: Dict[str, str] = client.get_score_api(address, hooks=hooks)
        print_result(result)

        return 0
