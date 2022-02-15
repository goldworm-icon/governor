# -*- coding: utf-8 -*-

from typing import List

import icon
from icon.data.address import Address
from icon.data.block_header import BlockHeader
from icon.data.validators import Validators
from icon.data.vote import Votes
from icon.utils import (
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
        block_header = BlockHeader(data)
        print_result(f"{block_header}")
        return 0


class VotesByHeightCommand(Command):
    def __init__(self):
        super().__init__(name="votesByHeight", readonly=True)
        self._hooks = {"request": print_request, "response": print_response}

    def init(self, sub_parser, common_parent_parser, invoke_parent_parser):
        desc = "icx_getVotesByHeight command"

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
        block_header = client.ex.get_block_header_by_height(height)

        bs: bytes = client.get_votes_by_height(height, hooks=hooks)
        votes = Votes.from_bytes(bs)
        addresses: List[Address] = votes.get_addresses(height, block_header.hash)
        for address in addresses:
            print(address)

        print("--------------------------------")

        client.ex.get_block_header_by_height(height)
        votes: Votes = client.ex.get_votes_by_height(height, hooks=hooks)
        print(votes)
        return 0


class ValidatorsByHeightCommand(Command):
    def __init__(self):
        super().__init__(name="validatorsByHeight", readonly=True)
        self._hooks = {"request": print_request, "response": print_response}

    def init(self, sub_parser, common_parent_parser, invoke_parent_parser):
        desc = "get validators in a block"

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
        validators: Validators = client.ex.get_validators_by_height(height, hooks=hooks)
        print_result(f"{validators}")
        return 0
