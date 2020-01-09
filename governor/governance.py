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
import os.path

from iconsdk.builder.call_builder import CallBuilder
from iconsdk.builder.transaction_builder import DeployTransactionBuilder, CallTransactionBuilder
from iconsdk.icon_service import IconService
from iconsdk.libs.in_memory_zip import gen_deploy_data_content
from iconsdk.providers.http_provider import HTTPProvider
from iconsdk.signed_transaction import SignedTransaction
from iconsdk.wallet.wallet import KeyWallet

from .constants import EOA_ADDRESS, GOVERNANCE_ADDRESS, ZERO_ADDRESS, COLUMN
from .utils import print_title, print_dict, get_url


def _print_request(title: str, content: dict):
    print_title(title, COLUMN)
    print_dict(content)
    print("")


class TxHandler:
    def __init__(self, service, nid: int, on_send_request: callable(dict)):
        self._icon_service = service
        self._nid = nid
        self._on_send_request = on_send_request

    def _deploy(self, owner, to, content, params, limit):
        transaction = DeployTransactionBuilder() \
            .from_(owner.get_address()) \
            .to(to) \
            .step_limit(limit) \
            .version(3) \
            .nid(self._nid) \
            .content_type("application/zip") \
            .content(content) \
            .params(params) \
            .build()

        ret = self._call_on_send_request(transaction.to_dict())
        if not ret:
            return

        return self._icon_service.send_transaction(SignedTransaction(transaction, owner))

    def _call_on_send_request(self, content: dict) -> bool:
        if self._on_send_request:
            return self._on_send_request(content)

        return False

    def install(self, owner, content, params=None, limit=0x50000000):
        return self._deploy(owner, ZERO_ADDRESS, content, params, limit)

    def update(self, owner, to, content, params=None, limit=0x80000000):
        return self._deploy(owner, to, content, params, limit)

    def invoke(self, owner, to, method, params, limit=0x10000000):
        transaction = CallTransactionBuilder() \
            .from_(owner.get_address()) \
            .to(to) \
            .step_limit(limit) \
            .nid(self._nid) \
            .method(method) \
            .params(params) \
            .build()

        self._call_on_send_request(transaction.to_dict())

        return self._icon_service.send_transaction(SignedTransaction(transaction, owner))


class GovernanceListener(object):
    def __init__(self):
        self._on_send_request = None

    def set_on_send_request(self, func: callable(dict)):
        self._on_send_request = func

    @property
    def on_send_request(self) -> callable(dict):
        return self._on_send_request


class GovernanceReader(GovernanceListener):
    def __init__(self, service, nid: int, address: str = EOA_ADDRESS):
        super().__init__()

        self._icon_service = service
        self._nid = nid
        self._from = address

    def _call(self, method, params=None):
        call = CallBuilder() \
            .from_(self._from) \
            .to(GOVERNANCE_ADDRESS) \
            .method(method) \
            .params(params) \
            .build()

        self.on_send_request(call.to_dict())

        return self._icon_service.call(call)

    def get_version(self):
        return self._call("getVersion")

    def get_revision(self):
        return self._call("getRevision")

    def get_service_config(self):
        return self._call("getServiceConfig")

    def get_score_status(self, address: str) -> dict:
        params = {"address": address}
        return self._call("getScoreStatus", params)

    def check_if_audit_enabled(self):
        service_config = self.get_service_config()
        if service_config['AUDIT'] == '0x1':
            return True
        else:
            return False

    def get_step_costs(self):
        return self._call(method="getStepCosts")

    def get_step_price(self):
        return self._call(method="getStepPrice")

    def get_tx_result(self, tx_hash: str) -> dict:
        tx_result = self._icon_service.get_transaction_result(tx_hash)
        return tx_result

    def get_max_step_limit(self, context_type: str) -> int:
        params = {"contextType": context_type}
        return self._call("getMaxStepLimit", params)

    def is_deployer(self, address: str) -> int:
        params = {"address": address}
        return self._call("isDeployer", params)

    def is_in_score_black_list(self, address: str) -> int:
        params = {"address": address}
        return self._call("isInScoreBlackList", params)

    def is_in_import_white_list(self, import_stmt: str) -> int:
        params = {"importStmt": import_stmt}
        return self._call("isInImportWhiteList", params)


class GovernanceWriter(GovernanceListener):
    def __init__(self, service, nid: int, owner):
        super().__init__()

        self._icon_service = service
        self._owner = owner
        self._nid = nid

    def _call(self, method: str, params: dict, step_limit: int = 0x10000000) -> str:
        tx_handler = self._create_tx_handler()
        return tx_handler.invoke(
            owner=self._owner,
            to=GOVERNANCE_ADDRESS,
            limit=step_limit,
            method=method,
            params=params
        )

    def _create_tx_handler(self) -> TxHandler:
        return TxHandler(self._icon_service, self._nid, self.on_send_request)

    def update(self, score_path: str) -> str:
        """Update governance SCORE

        :return: tx_hash
        """
        path: str = os.path.join(score_path, "package.json")
        if not os.path.isfile(path):
            raise Exception(f"Invalid score path: {score_path}")

        content: bytes = gen_deploy_data_content(score_path)

        tx_handler = self._create_tx_handler()
        ret = tx_handler.update(self._owner, GOVERNANCE_ADDRESS, content)

        return ret

    def accept_score(self, tx_hash: str) -> str:
        method = "acceptScore"
        params = {"txHash": tx_hash}

        return self._call(method, params)

    def reject_score(self, tx_hash: str, reason: str) -> str:
        method = "rejectScore"
        params = {"txHash": tx_hash, "reason": reason}

        return self._call(method, params)

    def add_auditor(self, address: str) -> str:
        method = "addAuditor"
        params = {"address": address}

        return self._call(method, params)

    def remove_auditor(self, address: str) -> str:
        method = "removeAuditor"
        params = {"address": address}

        return self._call(method, params)

    def set_revision(self, revision: int, name: str) -> str:
        """Set revision to governance SCORE

        :param revision:
        :param name:
        :return:
        """
        method = "setRevision"
        params = {"code": revision, "name": name}

        return self._call(method, params)

    def set_step_price(self, step_price: int) -> str:

        method = "setStepPrice"
        params = {"stepPrice": step_price}

        return self._call(method, params)

    def set_step_cost(self, step_type: str, cost: int) -> str:
        """
        URL: https://github.com/icon-project/governance#setstepcost

        :param step_type:
        :param cost:
        :return:
        """
        step_types = (
            "default", "contractCall", "contractCreate", "contractUpdate", "contractDestruct",
            "contractSet", "get", "set", "replace", "delete", "input", "eventlog", "apiCall"
        )

        if step_type not in step_types:
            raise ValueError(f"Invalid stepType: {step_type}")

        method = "setStepCost"
        params = {
            "stepType": step_type,
            "cost": cost
        }

        return self._call(method, params)

    def set_max_step_limit(self, context_type: str, value: int) -> str:

        context_types = ("invoke", "query")

        if context_type not in context_types:
            raise ValueError(f"Invalid contextType: {context_type}")

        method = "setMaxStepLimit"
        params = {"contextType": context_type, "value": value}

        return self._call(method, params)

    def add_deployer(self, address: str) -> str:

        method = "addDeployer"
        params = {"address": address}

        return self._call(method, params)

    def remove_deployer(self, address: str) -> str:

        method = "removeDeployer"
        params = {"address": address}

        return self._call(method, params)

    def add_to_score_black_list(self, address: str) -> str:

        method = "addToScoreBlackList"
        params = {"address": address}

        return self._call(method, params)

    def remove_from_score_black_list(self, address: str) -> str:

        method = "removeFromScoreBlackList"
        params = {"address": address}

        return self._call(method, params)

    def add_import_white_list(self, import_stmt: str) -> str:

        method = "addImportWhiteList"
        params = {"importStmt": import_stmt}

        return self._call(method, params)

    def remove_import_white_list(self, import_stmt: str) -> str:

        method = "removeImportWhiteList"
        params = {"importStmt": import_stmt}

        return self._call(method, params)

    def update_service_config(self, service_flag: int):

        method = "updateServiceConfig"
        params = {"serviceFlag": service_flag}

        return self._call(method, params)

    def get_tx_result(self, tx_hash: str) -> dict:
        tx_result = self._icon_service.get_transaction_result(tx_hash)
        return tx_result


def create_reader_by_args(args) -> GovernanceReader:
    url: str = get_url(args.url)
    nid: int = args.nid

    reader = create_reader(url, nid)

    callback = functools.partial(_print_request, "Request")
    reader.set_on_send_request(callback)

    return reader


def create_reader(url: str, nid: int) -> GovernanceReader:
    url: str = get_url(url)
    icon_service = IconService(HTTPProvider(url))
    return GovernanceReader(icon_service, nid)


def create_writer_by_args(args) -> GovernanceWriter:
    url: str = get_url(args.url)
    nid: int = args.nid
    keystore_path: str = args.keystore
    password: str = args.password
    yes: bool = args.yes

    if password is None:
        password = getpass.getpass("> Password: ")

    writer = create_writer(url, nid, keystore_path, password)

    callback = functools.partial(_confirm_callback, yes=yes)
    writer.set_on_send_request(callback)

    return writer


def create_writer(url: str, nid: int, keystore_path: str, password: str) -> GovernanceWriter:
    url: str = get_url(url)
    icon_service = IconService(HTTPProvider(url))

    owner_wallet = KeyWallet.load(keystore_path, password)
    return GovernanceWriter(icon_service, nid, owner_wallet)


def create_icon_service(url: str) -> IconService:
    url: str = get_url(url)
    return IconService(HTTPProvider(url))


def _confirm_callback(content: dict, yes: bool) -> bool:
    _print_request("Request", content)

    if not yes:
        ret: str = input("> Continue? [Y/n]")
        if ret == "n":
            return False

    return True
