# -*- coding: utf-8 -*-


from typing import Optional

import icon
from icon.data import Block, hex_to_bytes

from .command import Command
from ..utils import (
    print_request,
    print_response,
    print_result,
    resolve_url
)


class BlockCommand(Command):
    def __init__(self):
        self._name = "block"
        self._hooks = {"request": print_request, "response": print_response}

    def init(self, sub_parser, common_parent_parser, invoke_parent_parser):
        desc = "icx_getBlockByHash, icx_getBlockByHeight and icx_lastBlock commands"

        score_parser = sub_parser.add_parser(
            self._name, parents=[common_parent_parser], help=desc
        )

        score_parser.add_argument(
            "value", type=str, nargs="?", default=None, help="block_hash or block_height",
        )

        score_parser.set_defaults(func=self._run)

    @property
    def name(self) -> str:
        return self._name

    def _run(self, args) -> int:
        url: str = resolve_url(args.url)
        value: Optional[str] = args.value

        if isinstance(value, str):
            if value.startswith("0x") and len(value) == 66:
                value: bytes = hex_to_bytes(value)
            else:
                value: int = int(value, 0)

        client: icon.Client = icon.create_client(url)
        if isinstance(value, bytes):
            block: Block = client.get_block_by_hash(value, hooks=self._hooks)
        elif isinstance(value, int):
            block: Block = client.get_block_by_height(value, hooks=self._hooks)
        else:
            block: Block = client.get_last_block(hooks=self._hooks)

        print_result(f"{block}")

        return 0
