# Copyright 2019 ICON Foundation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import functools
import getpass
import logging
import os.path
from typing import Dict, Union, Any, Optional

import icon
from icon.builder import CallBuilder, CallTransactionBuilder, DeployTransactionBuilder
from icon.data import (
    Address,
    GOVERNANCE_SCORE_ADDRESS,
    SYSTEM_SCORE_ADDRESS,
    TransactionResult,
)
from icon.wallet import KeyWallet

from ..constants import COLUMN, EOA_ADDRESS
from ..utils import (
    print_dict,
    print_title,
    resolve_nid,
    resolve_url,
)


def _print_request(title: str, content: dict):
    print_title(title, COLUMN)
    print_dict(content)
    print("")


class GovernanceListener(object):
    def __init__(self):
        self._on_send_request = None

    def set_on_send_request(self, func: callable(Dict[str, str])):
        self._on_send_request = func

    @property
    def on_send_request(self) -> callable(Dict[str, str]):
        return self._on_send_request


class GovernanceReader(GovernanceListener):
    def __init__(self, client: icon.Client, nid: int, address: Address = EOA_ADDRESS):
        super().__init__()

        self._client = client
        self._nid = nid
        self._from = address

    def _call(self, method, params=None) -> Union[str, Dict[str, str]]:
        params: Dict[str, str] = (
            CallBuilder()
            .from_(self._from)
            .to(GOVERNANCE_SCORE_ADDRESS)
            .call_data(method, params)
            .build()
        )

        self.on_send_request(params)
        return self._client.call(params)

    def get_version(self) -> str:
        return self._call("getVersion")

    def get_revision(self) -> Dict[str, str]:
        return self._call("getRevision")

    def get_service_config(self) -> Dict[str, str]:
        return self._call("getServiceConfig")

    def get_score_status(self, address: Address) -> Dict[str, str]:
        params = {"address": address}
        return self._call("getScoreStatus", params)

    def check_if_audit_enabled(self) -> bool:
        service_config = self.get_service_config()
        return service_config["AUDIT"] == "0x1"

    def get_step_costs(self) -> Dict[str, str]:
        return self._call(method="getStepCosts")

    def get_step_price(self) -> int:
        ret: str = self._call(method="getStepPrice")
        return int(ret, base=0)

    def get_tx_result(self, tx_hash: bytes) -> TransactionResult:
        return self._client.get_transaction_result(tx_hash)

    def get_max_step_limit(self, context_type: str) -> int:
        """

        :param context_type: "invoke" or "query"
        :return: maximum step limit
        """
        params = {"contextType": context_type}
        ret: str = self._call("getMaxStepLimit", params)
        return int(ret, base=0)

    def is_deployer(self, address: str) -> bool:
        params = {"address": address}
        ret: str = self._call("isDeployer", params)
        return bool(int(ret, base=0))

    def is_in_score_black_list(self, address: str) -> bool:
        params = {"address": address}
        ret: str = self._call("isInScoreBlackList", params)
        return bool(int(ret, base=0))

    def is_in_import_white_list(self, import_stmt: str) -> bool:
        params = {"importStmt": import_stmt}
        ret: str = self._call("isInImportWhiteList", params)
        return bool(int(ret, base=0))


class GovernanceWriter(GovernanceListener):
    def __init__(
        self,
        client: icon.Client,
        nid: int,
        owner: KeyWallet,
        step_limit: int,
        estimate: bool,
    ):
        super().__init__()

        self._client = client
        self._owner = owner
        self._nid = nid
        self._step_limit = step_limit
        self._estimate = estimate

    def _create_call_tx(
        self, method: str, params: Dict[str, Any]
    ) -> icon.builder.Transaction:
        return (
            CallTransactionBuilder()
            .nid(self._nid)
            .from_(self._owner.address)
            .to(GOVERNANCE_SCORE_ADDRESS)
            .step_limit(self._step_limit)
            .call_data(method, params)
            .build()
        )

    def _create_deploy_tx(
        self, score_path: str, update: bool
    ) -> icon.builder.Transaction:
        to = GOVERNANCE_SCORE_ADDRESS if update else SYSTEM_SCORE_ADDRESS

        return (
            DeployTransactionBuilder()
            .nid(self._nid)
            .from_(self._owner.address)
            .to(to)
            .step_limit(self._step_limit)
            .deploy_data_from_path(score_path, params=None)
            .build()
        )

    def _run(self, tx: icon.builder.Transaction) -> Union[int, bytes]:
        logging.debug(f"_run() start: tx={tx}")

        self.on_send_request(tx)
        ret = self._send_transaction(tx)

        logging.debug(f"_run() end")
        return ret

    def _call(self, method: str, params: Optional[Dict[str, Any]]) -> Union[int, bytes]:
        logging.debug(f"_call() start: method={method} params={params}")

        tx: icon.builder.Transaction = self._create_call_tx(method, params)
        ret = self._run(tx)

        logging.debug("_call() end")
        return ret

    def _send_transaction(self, tx: icon.builder.Transaction) -> bytes:
        logging.debug(f"_send_transaction() start")

        if not self._estimate:
            tx.sign(self._owner.private_key)

        ret = self._client.send_transaction(tx, estimate=self._estimate)

        logging.debug(f"_send_transaction() end")
        return ret

    def deploy(self, path: str) -> Union[int, bytes]:
        """Update governance SCORE

        :return: tx_hash
        """
        logging.debug(f"deploy() start: path={path}")

        path: str = os.path.join(path, "package.json")
        if not os.path.isfile(path):
            raise Exception(f"Invalid score path: {path}")

        tx: icon.builder.Transaction = self._create_deploy_tx(path, update=True)
        ret = self._run(tx)

        logging.debug(f"deploy() end")
        return ret

    def accept_score(self, tx_hash: str) -> bytes:
        method = "acceptScore"
        params = {"txHash": tx_hash}

        return self._call(method, params)

    def reject_score(self, tx_hash: str, reason: str) -> bytes:
        method = "rejectScore"
        params = {"txHash": tx_hash, "reason": reason}

        return self._call(method, params)

    def add_auditor(self, address: str) -> bytes:
        method = "addAuditor"
        params = {"address": address}

        return self._call(method, params)

    def remove_auditor(self, address: str) -> bytes:
        method = "removeAuditor"
        params = {"address": address}

        return self._call(method, params)

    def set_revision(self, revision: int, name: str) -> bytes:
        """Set revision to governance SCORE

        :param revision:
        :param name:
        :return:
        """
        method = "setRevision"
        params = {"code": revision, "name": name}

        return self._call(method, params)

    def set_step_price(self, step_price: int) -> bytes:
        logging.debug(f"set_step_price() start: step_price={step_price}")

        method = "setStepPrice"
        params = {"stepPrice": step_price}

        ret = self._call(method, params)
        logging.debug(f"set_step_price() end")

        return ret

    def set_step_cost(self, step_type: str, cost: int) -> bytes:
        """
        URL: https://github.com/icon-project/governance#setstepcost

        :param step_type:
        :param cost:
        :return:
        """
        step_types = (
            "default",
            "contractCall",
            "contractCreate",
            "contractUpdate",
            "contractDestruct",
            "contractSet",
            "get",
            "set",
            "replace",
            "delete",
            "input",
            "eventlog",
            "apiCall",
        )

        if step_type not in step_types:
            raise ValueError(f"Invalid stepType: {step_type}")

        method = "setStepCost"
        params = {"stepType": step_type, "cost": cost}

        return self._call(method, params)

    def set_max_step_limit(self, context_type: str, value: int) -> bytes:

        context_types = ("invoke", "query")

        if context_type not in context_types:
            raise ValueError(f"Invalid contextType: {context_type}")

        method = "setMaxStepLimit"
        params = {"contextType": context_type, "value": value}

        return self._call(method, params)

    def add_deployer(self, address: str) -> bytes:

        method = "addDeployer"
        params = {"address": address}

        return self._call(method, params)

    def remove_deployer(self, address: str) -> bytes:

        method = "removeDeployer"
        params = {"address": address}

        return self._call(method, params)

    def add_to_score_black_list(self, address: str) -> bytes:

        method = "addToScoreBlackList"
        params = {"address": address}

        return self._call(method, params)

    def remove_from_score_black_list(self, address: str) -> bytes:

        method = "removeFromScoreBlackList"
        params = {"address": address}

        return self._call(method, params)

    def add_import_white_list(self, import_stmt: str) -> bytes:

        method = "addImportWhiteList"
        params = {"importStmt": import_stmt}

        return self._call(method, params)

    def remove_import_white_list(self, import_stmt: str) -> bytes:

        method = "removeImportWhiteList"
        params = {"importStmt": import_stmt}

        return self._call(method, params)

    def update_service_config(self, service_flag: int) -> bytes:

        method = "updateServiceConfig"
        params = {"serviceFlag": service_flag}

        return self._call(method, params)

    def get_tx_result(self, tx_hash: bytes) -> TransactionResult:
        tx_result = self._client.get_transaction_result(tx_hash)
        return tx_result


def create_reader_by_args(args) -> GovernanceReader:
    url: str = resolve_url(args.url)
    nid: int = resolve_nid(args.nid, args.url)

    reader = create_reader(url, nid)

    callback = functools.partial(_print_request, "Request")
    reader.set_on_send_request(callback)

    return reader


def create_reader(url: str, nid: int) -> GovernanceReader:
    client = icon.create_client(url)
    return GovernanceReader(client, nid)


def create_writer_by_args(args) -> GovernanceWriter:
    url: str = resolve_url(args.url)
    nid: int = resolve_nid(args.nid, args.url)
    step_limit: int = args.step_limit
    keystore_path: str = args.keystore
    password: str = args.password
    yes: bool = args.yes
    estimate: bool = args.estimate

    if password is None:
        password = getpass.getpass("> Password: ")

    writer = create_writer(url, nid, keystore_path, password, step_limit, estimate)

    callback = functools.partial(_confirm_callback, yes=yes)
    writer.set_on_send_request(callback)

    return writer


def create_writer(
    url: str,
    nid: int,
    keystore_path: str,
    password: str,
    step_limit: int,
    estimate: bool,
) -> GovernanceWriter:
    client = icon.create_client(url)

    owner_wallet = KeyWallet.load(keystore_path, password)
    return GovernanceWriter(client, nid, owner_wallet, step_limit, estimate)


def _confirm_callback(request: Dict[str, str], yes: bool) -> bool:
    _print_request("Request", request)

    if not yes:
        ret: str = input("> Continue? [Y/n]")
        if ret == "n":
            return False

    return True
