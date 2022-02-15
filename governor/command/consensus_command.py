# -*- coding: utf-8 -*-
import sys
from collections import defaultdict
from typing import Dict
from typing import List

import plyvel

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
    get_hooks_from_args,
    print_result,
    resolve_url
)


class DataByHashCommand(Command):
    def __init__(self):
        super().__init__(name="dataByHash", readonly=True)

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
        hooks = get_hooks_from_args(args)

        if data_hash.startswith("0x") and len(data_hash) == 66:
            data_hash: bytes = hex_to_bytes(data_hash)
        else:
            raise ValueError("Invalid data_hash")

        client: icon.Client = icon.create_client(url)
        data: bytes = client.get_data_by_hash(data_hash, hooks=hooks)
        print_result(f"{bytes_to_hex(data)}")
        return 0


class BlockHeaderByHashCommand(Command):
    def __init__(self):
        super().__init__(name="blockHeaderByHash", readonly=True)

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
        hooks = get_hooks_from_args(args)

        client: icon.Client = icon.create_client(url)
        data: bytes = client.get_block_header_by_height(height, hooks=hooks)
        block_header = BlockHeader(data)
        print_result(f"{block_header}")
        return 0


class VotesByHeightCommand(Command):
    def __init__(self):
        super().__init__(name="votesByHeight", readonly=True)

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
        url: str = resolve_url(args.url)
        height: int = str_to_int(args.height)
        hooks = get_hooks_from_args(args)

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


class ConsensusInfoCommand(Command):
    def __init__(self):
        super().__init__(name="consensusInfo", readonly=True)

    def init(self, sub_parser, common_parent_parser, invoke_parent_parser):
        desc = "Collect consensusInfo data (validators and votes) from a given range of blocks"

        score_parser = sub_parser.add_parser(
            self.name, parents=[common_parent_parser], help=desc
        )
        score_parser.add_argument(
            "start", type=str, nargs="?", default=None, help="start block height"
        )
        score_parser.add_argument(
            "end", type=str, nargs="?", default=None, help="end block height"
        )
        score_parser.add_argument(
            "--db", type=str, default="consensus", help="the path of db to store consensus info"
        )
        score_parser.add_argument(
            "--record", action="store_true", help="write data to db"
        )
        score_parser.add_argument(
            "--check", action="store_true", help="inspect db"
        )
        score_parser.set_defaults(func=self._run)

    def _run(self, args) -> int:
        url: str = resolve_url(args.url)
        start: int = str_to_int(args.start)
        end: int = str_to_int(args.end)
        hooks = get_hooks_from_args(args)

        client: icon.Client = icon.create_client(url)
        db = plyvel.DB(args.db, create_if_missing=True)
        if args.record:
            self._write_to_db(client, db, start, end, hooks)
        if args.check:
            self._check(db)
        db.close()
        return 0

    def _write_to_db(self, client: icon.Client, db: plyvel.DB, start: int, end: int, hooks):
        for height in range(start, end + 1):
            print(height, file=sys.stderr, flush=True)
            block_header = client.ex.get_block_header_by_height(height)
            bs: bytes = client.get_votes_by_height(height, hooks=hooks)
            votes = Votes.from_bytes(bs)
            validators: Validators = client.ex.get_validators_by_height(height, hooks=hooks)
            self._write_one(db, block_header, validators, votes)

    def _write_one(self, db: plyvel.DB, block_header: BlockHeader, validators: Validators, votes: Votes):
        height: int = block_header.height
        ba = bytearray(b"\x00" + height.to_bytes(8, "big", signed=False))

        with db.write_batch() as wb:
            ba[0] = 0
            wb.put(bytes(ba), block_header.hash)
            ba[0] = 1
            db.put(bytes(ba), bytes(validators))
            ba[0] = 2
            db.put(bytes(ba), bytes(votes))

    def _check(self, db: plyvel.DB):

        hash_db = db.prefixed_db(b'\x00')
        validators_db = db.prefixed_db(b'\x01')
        votes_db = db.prefixed_db(b'\x02')

        vote_map: Dict[Address, int] = defaultdict(int)
        nil_vote_map: Dict[Address, int] = defaultdict(int)
        nil_vote_map_in_term: Dict[Address, int] = defaultdict(int)
        prev_validators = None
        prev_height = 0
        term_start_block = 2534401

        for key, block_hash in hash_db:
            nil_voters = []
            height = int.from_bytes(key, "big")
            if prev_height > 0 and height != prev_height + 1:
                print(f"Error: Invalid height: {prev_height} {height}")
                return
            prev_height = height

            validators = Validators.from_bytes(validators_db.get(key))
            votes = Votes.from_bytes(votes_db.get(key))

            print(f"{height} -------------------------------")
            print(f"{height} -------------------------------", file=sys.stderr, flush=True)

            q, r = divmod(height - term_start_block, 7200)
            if r == 0:
                print(f"term begins: seq={q}")
                nil_vote_map_in_term.clear()

            voters: List[Address] = votes.get_addresses(height, block_hash)
            for voter in voters:
                vote_map[voter] += 1

            for validator in validators.addresses:
                if validator not in voters:
                    nil_vote_map[validator] += 1
                    nil_vote_map_in_term[validator] += 1
                    nil_voters.append(validator)

            if prev_validators is None or prev_validators != validators:
                prev_validators = validators
                print("validator changed")
            # Print validators
            print(f"> validators\n{validators}\n")

            # Print voters
            voters_text = "\n".join((str(voter) for voter in voters))
            print(f"> voters\n{voters_text}")

            # Print nil voters
            nil_voters_text = "\n".join((
                f"{nil_voter}: {nil_vote_map_in_term[nil_voter]}, {nil_vote_map[nil_voter]}"
                for nil_voter in nil_voters
            ))
            print(f"> nil_voters\n{nil_voters_text}", flush=True)

        print("Result ------------------------------")
        print("votes")
        print("\n".join((
            f"{address}: {count}" for address, count in vote_map.items()
        )))
        print("nil_votes")
        print("\n".join((
            f"{address}: {count}" for address, count in nil_vote_map.items()
        )))
