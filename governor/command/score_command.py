import functools
import json
import os
from typing import Dict, Any, Optional

import icon
from icon.builder import (
    DeployTransactionBuilder,
)
from icon.data import (
    Address,
    SYSTEM_SCORE_ADDRESS,
)
from icon.data.utils import (
    hex_to_bytes
)
from icon.wallet import (
    KeyWallet
)

from .command import Command
from ..utils import (
    confirm_transaction,
    print_request,
    print_response,
    resolve_address,
    resolve_nid,
    resolve_url,
    resolve_wallet,
)


class DeployCommand(Command):
    def __init__(self):
        super().__init__(name="deploy", readonly=False)

    def init(self, sub_parser, common_parent_parser, invoke_parent_parser):
        desc = "Install or update governance SCORE"

        score_parser = sub_parser.add_parser(
            self.name,
            parents=[common_parent_parser, invoke_parent_parser],
            help=desc
        )

        score_parser.add_argument(
            "score_path",
            type=str,
            nargs="?",
            help="score path\nex) ./abc_score",
        )
        score_parser.add_argument(
            "--to",
            type=str,
            nargs="?",
            metavar="score_address",
            default=SYSTEM_SCORE_ADDRESS,
            help="score address to update or system score will be used as default",
        )
        score_parser.add_argument(
            "--params",
            type=str,
            nargs="?",
            default=None,
            help='params for deploy a score: ex) {"a":1,"b":"hello"}',
        )

        score_parser.set_defaults(func=self._run)

    @classmethod
    def _run(cls, args) -> bytes:
        url: str = resolve_url(args.url)
        nid: int = resolve_nid(args.nid, args.url)
        score_path: str = args.score_path
        wallet: KeyWallet = resolve_wallet(args)
        to: Address = resolve_address(args.to)
        step_limit: int = args.step_limit

        hooks = {
            "request": functools.partial(confirm_transaction, yes=args.yes),
            "response": print_response
        }

        path: str = os.path.join(score_path, "package.json")
        if not os.path.isfile(path):
            raise Exception(f"Invalid score path: {path}")

        params: Optional[Dict[str, Any]] = None
        if isinstance(args.params, str):
            params = cls._get_score_params(args.params)

        builder = (
            DeployTransactionBuilder()
            .nid(nid)
            .from_(wallet.address)
            .to(to)
            .deploy_data_from_path(score_path, params=params)
        )

        client: icon.Client = icon.create_client(url)

        if step_limit <= 0:
            tx = builder.build()
            step_limit = client.estimate_step(tx, hooks=hooks) * 12 // 10

        builder.step_limit(step_limit)
        tx = builder.build()
        tx.sign(wallet.private_key)

        return client.send_transaction(tx, hooks=hooks)

    @classmethod
    def _get_score_params(cls, value: str) -> Dict[str, Any]:
        try:
            fp = open(value, mode="rt")
            params = json.load(fp)
            fp.close()
            return params
        except:
            return json.loads(value)


class DownloadCommand(Command):
    def __init__(self):
        super().__init__(name="download", readonly=True)

    def init(self, sub_parser, common_parent_parser, invoke_parent_parser):
        desc = "Download score code"

        parser = sub_parser.add_parser(
            self.name,
            parents=[common_parent_parser],
            help=desc
        )

        parser.add_argument(
            "tx_hash",
            type=str,
            help="score addresses to download"
        )
        parser.set_defaults(func=self._run)

    def _run(self, args):
        url: str = resolve_url(args.url)
        tx_hash: bytes = hex_to_bytes(args.tx_hash)
        path: str = self._get_path(args)
        hooks = {"request": print_request, "response": print_response}

        client: icon.Client = icon.create_client(url)
        tx: icon.data.Transaction = client.get_transaction(tx_hash, hooks=hooks)
        content: bytes = hex_to_bytes(tx.data["content"])

        f = open(path, "wb")
        f.write(content)
        f.close()

    @classmethod
    def _get_path(cls, args) -> str:
        return f"{args.tx_hash}.zip"
