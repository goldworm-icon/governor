# -*- coding: utf-8 -*-

import icon
from icon.data import (
    bytes_to_hex,
    hex_to_bytes,
    str_to_int,
)

from .command import Command
from ..utils import (
    print_request,
    print_response,
    print_result,
    resolve_url
)


class DataByHashCommand(Command):
    def __init__(self):
        super().__init__(name="dataByHash", readonly=True)
        self._hooks = {"request": print_request, "response": print_response}

    def init(self, sub_parser, common_parent_parser, invoke_parent_parser):
        desc = "icx_getDataByHash command"

        score_parser = sub_parser.add_parser(
            self.name, parents=[common_parent_parser], help=desc
        )
        score_parser.add_argument(
            "data_hash", type=str, nargs="?", default=None, help="data_hash"
        )
        score_parser.set_defaults(func=self._run)

    def _run(self, args) -> int:
        url: str = resolve_url(args.url)
        data_hash: str = args.data_hash

        if data_hash.startswith("0x") and len(data_hash) == 66:
            data_hash: bytes = hex_to_bytes(data_hash)
        else:
            raise ValueError("Invalid data_hash")

        client: icon.Client = icon.create_client(url)
        data: bytes = client.get_data_by_hash(data_hash, hooks=self._hooks)
        print_result(f"{bytes_to_hex(data)}")
        return 0


class BlockHeaderByHashCommand(Command):
    def __init__(self):
        super().__init__(name="blockHeaderByHash", readonly=True)
        self._hooks = {"request": print_request, "response": print_response}

    def init(self, sub_parser, common_parent_parser, invoke_parent_parser):
        desc = "icx_getBlockHeaderByHash command"

        score_parser = sub_parser.add_parser(
            self.name, parents=[common_parent_parser], help=desc
        )
        score_parser.add_argument(
            "height", type=str, nargs="?", default=None, help="block height"
        )
        score_parser.set_defaults(func=self._run)

    def _run(self, args) -> int:
        url: str = resolve_url(args.url)
        height: int = str_to_int(args.height)

        client: icon.Client = icon.create_client(url)
        data: bytes = client.get_block_header_by_height(height, hooks=self._hooks)
        print_result(f"{bytes_to_hex(data)}")
        return 0


class VotesByHashCommand(Command):
    def __init__(self):
        super().__init__(name="votesByHash", readonly=True)
        self._hooks = {"request": print_request, "response": print_response}

    def init(self, sub_parser, common_parent_parser, invoke_parent_parser):
        desc = "icx_getVotesByHash command"

        score_parser = sub_parser.add_parser(
            self.name, parents=[common_parent_parser], help=desc
        )
        score_parser.add_argument(
            "height", type=str, nargs="?", default=None, help="block height"
        )
        score_parser.set_defaults(func=self._run)

    def _run(self, args) -> int:
        verbose: bool = args.verbose
        url: str = resolve_url(args.url)
        height: int = str_to_int(args.height)
        if verbose:
            hooks = self._hooks
        else:
            hooks = {}

        client: icon.Client = icon.create_client(url)
        data: bytes = client.get_votes_by_height(height, hooks=hooks)
        print_result(f"{bytes_to_hex(data)}")
        return 0
