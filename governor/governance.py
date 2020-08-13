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
from typing import Dict, Union, Any
from urllib.parse import urlparse

import icon
from .constants import EOA_ADDRESS, GOVERNANCE_ADDRESS, ZERO_ADDRESS, COLUMN
from .utils import print_title, print_dict, resolve_url, get_predefined_nid


def _print_request(title: str, content: dict):
    print_title(title, COLUMN)
    print_dict(content)
    print("")


class TxBuildHelper:
    def __init__(self, client: icon.Client, nid: int):
        self._client: icon.Client = client
        self._nid = nid

    def _deploy(
        self, owner: icon.KeyWallet, to: icon.Address, path: str, params, step_limit
    ) -> Dict[str, str]:
        logging.debug("TxBuildHelper._deploy() start")

        transaction: Dict[str, str] = (
            icon.DeployTransactionBuilder()
            .from_(owner.address)
            .to(to)
            .step_limit(step_limit)
            .version(3)
            .nid(self._nid)
            .content_from_path(path)
            .params(params)
            .build()
        )

        logging.debug("TxBuildHelper._deploy() end")
        return transaction

    def install(
        self, owner: icon.KeyWallet, path: str, params=None, step_limit=0x50000000
    ) -> Dict[str, str]:
        return self._deploy(owner, ZERO_ADDRESS, path, params, step_limit)

    def update(
        self,
        owner: icon.KeyWallet,
        to: icon.Address,
        path: str,
        params=None,
        step_limit=0x80000000,
    ) -> Dict[str, str]:
        transaction = self._deploy(owner, to, path, params, step_limit)

        return transaction

    def invoke(self, owner: icon.KeyWallet, to, method, params, step_limit=0x10000000):
        return (
            icon.CallTransactionBuilder(method)
            .from_(owner.address)
            .to(to)
            .step_limit(step_limit)
            .nid(self._nid)
            .params(params)
            .build()
        )


class TxHandler:
    def __init__(
        self, client: icon.Client, nid: int, on_send_request: callable(Dict[str, str])
    ):
        self._client = client
        self._nid = nid
        self._on_send_request = on_send_request
        self._tx_build_helper = TxBuildHelper(client, nid)

    def _call_on_send_request(self, content: Dict[str, str]) -> bool:
        if self._on_send_request:
            return self._on_send_request(content)

        return False

    def install(
        self,
        owner: icon.KeyWallet,
        path: str,
        params=None,
        step_limit=0x50000000,
        estimate: bool = False,
    ):

        transaction: Dict[str, str] = self._tx_build_helper.install(
            owner, path, params, step_limit
        )
        return self._run(transaction, owner, estimate)

    def update(
        self,
        owner: icon.KeyWallet,
        to: icon.Address,
        path: str,
        params=None,
        step_limit=0x70000000,
        estimate: bool = False,
    ):
        transaction: Dict[str, str] = self._tx_build_helper.update(
            owner, to, path, params, step_limit
        )
        return self._run(transaction, owner, estimate)

    def invoke(
        self,
        owner: icon.KeyWallet,
        to: icon.Address,
        method: str,
        params: Dict[str, Any],
        step_limit=0x10000000,
        estimate: bool = False,
    ):
        transaction: Dict[str, str] = self._tx_build_helper.invoke(
            owner, to, method, params, step_limit
        )
        return self._run(transaction, owner, estimate)

    def _run(
        self, params: Dict[str, str], owner: icon.KeyWallet, estimate: bool
    ) -> Union[int, bytes]:
        logging.debug("TxHandler._run() start")

        if estimate:
            ret: int = self._estimate_step(params)
        else:
            ret: bytes = self._send_transaction(owner, params)

        logging.debug("TxHandler._run() end")
        return ret

    def _send_transaction(self, owner: icon.KeyWallet, params: Dict[str, str]) -> bytes:
        logging.debug("TxHandler._send_transaction() start")

        ret = self._call_on_send_request(params)
        if ret:
            ret = self._client.send_transaction(params, owner.private_key)

        logging.debug("TxHandler._send_transaction() end")
        return ret

    def _estimate_step(self, params: Dict[str, str]) -> int:
        logging.debug("TxHandler._estimate_step() start")
        ret = self._client.estimate_step(params)
        logging.debug("TxHandler._estimate_step() end")

        return ret


class GovernanceListener(object):
    def __init__(self):
        self._on_send_request = None

    def set_on_send_request(self, func: callable(dict)):
        self._on_send_request = func

    @property
    def on_send_request(self) -> callable(dict):
        return self._on_send_request


class GovernanceReader(GovernanceListener):
    def __init__(
        self, client: icon.Client, nid: int, address: icon.Address = EOA_ADDRESS
    ):
        super().__init__()

        self._client = client
        self._nid = nid
        self._from = address

    def _call(self, method, params=None) -> Union[str, Dict[str, str]]:
        params: Dict[str, str] = icon.CallBuilder(method).from_(self._from).to(
            GOVERNANCE_ADDRESS
        ).params(params).build()

        self.on_send_request(params)

        return self._client.call(params)

    def get_version(self) -> str:
        return self._call("getVersion")

    def get_revision(self) -> Dict[str, str]:
        return self._call("getRevision")

    def get_service_config(self) -> Dict[str, str]:
        return self._call("getServiceConfig")

    def get_score_status(self, address: icon.Address) -> Dict[str, str]:
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

    def get_tx_result(self, tx_hash: bytes) -> icon.TransactionResult:
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
    def __init__(self, client: icon.Client, nid: int, owner, step_limit: int):
        super().__init__()

        self._client = client
        self._owner = owner
        self._nid = nid
        self._step_limit = step_limit

    def _call(self, method: str, params: Dict[str, Any]) -> bytes:
        tx_handler = self._create_tx_handler()
        return tx_handler.invoke(
            owner=self._owner,
            to=GOVERNANCE_ADDRESS,
            step_limit=self._step_limit,
            method=method,
            params=params,
        )

    def _create_tx_handler(self) -> TxHandler:
        return TxHandler(self._client, self._nid, self.on_send_request)

    def update(self, score_path: str, estimate: bool) -> Union[int, bytes]:
        """Update governance SCORE

        :return: tx_hash
        """
        path: str = os.path.join(score_path, "package.json")
        if not os.path.isfile(path):
            raise Exception(f"Invalid score path: {score_path}")

        tx_handler = self._create_tx_handler()
        return tx_handler.update(
            self._owner,
            GOVERNANCE_ADDRESS,
            score_path,
            step_limit=self._step_limit,
            estimate=estimate,
        )

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

        method = "setStepPrice"
        params = {"stepPrice": step_price}

        return self._call(method, params)

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

    def get_tx_result(self, tx_hash: bytes) -> icon.TransactionResult:
        tx_result = self._client.get_transaction_result(tx_hash)
        return tx_result


def create_reader_by_args(args) -> GovernanceReader:
    url: str = resolve_url(args.url)
    nid: int = _get_nid(args)

    reader = create_reader(url, nid)

    callback = functools.partial(_print_request, "Request")
    reader.set_on_send_request(callback)

    return reader


def create_reader(url: str, nid: int) -> GovernanceReader:
    client = create_client(url)
    return GovernanceReader(client, nid)


def create_writer_by_args(args) -> GovernanceWriter:
    url: str = resolve_url(args.url)
    nid: int = _get_nid(args)
    step_limit: int = args.step_limit
    keystore_path: str = args.keystore
    password: str = args.password
    yes: bool = args.yes

    if password is None:
        password = getpass.getpass("> Password: ")

    writer = create_writer(url, nid, keystore_path, password, step_limit)

    callback = functools.partial(_confirm_callback, yes=yes)
    writer.set_on_send_request(callback)

    return writer


def create_writer(
    url: str, nid: int, keystore_path: str, password: str, step_limit: int
) -> GovernanceWriter:
    client = create_client(url)

    owner_wallet = icon.KeyWallet.load(keystore_path, password)
    return GovernanceWriter(client, nid, owner_wallet, step_limit)


def create_client(url: str) -> icon.Client:
    o = urlparse(url)
    return icon.Client(icon.HTTPProvider(f"{o.scheme}://{o.netloc}", 3))


def _confirm_callback(content: dict, yes: bool) -> bool:
    _print_request("Request", content)

    if not yes:
        ret: str = input("> Continue? [Y/n]")
        if ret == "n":
            return False

    return True


def _get_nid(args) -> int:
    nid: int = args.nid

    if nid < 0:
        nid = get_predefined_nid(args.url)
        if nid < 0:
            ValueError("nid is required")

    return nid
