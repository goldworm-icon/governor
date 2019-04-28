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

import json
from time import sleep
import getpass

from iconsdk.builder.call_builder import CallBuilder
from iconsdk.builder.transaction_builder import DeployTransactionBuilder, CallTransactionBuilder
from iconsdk.exception import JSONRPCException
from iconsdk.icon_service import IconService
from iconsdk.libs.in_memory_zip import gen_deploy_data_content
from iconsdk.providers.http_provider import HTTPProvider
from iconsdk.signed_transaction import SignedTransaction
from iconsdk.wallet.wallet import KeyWallet

from .constants import EOA_ADDRESS, GOVERNANCE_ADDRESS, ZERO_ADDRESS


def print_response(header, msg):
    print(f'{header}: {json.dumps(msg, indent=4)}')


class TxHandler:
    def __init__(self, service, nid: int):
        self._icon_service = service
        self._nid = nid

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
        return self._icon_service.send_transaction(SignedTransaction(transaction, owner))

    def install(self, owner, content, params=None, limit=0x50000000):
        return self._deploy(owner, ZERO_ADDRESS, content, params, limit)

    def update(self, owner, to, content, params=None, limit=0x70000000):
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
        return self._icon_service.send_transaction(SignedTransaction(transaction, owner))

    def get_tx_result(self, tx_hash):
        while True:
            try:
                tx_result = self._icon_service.get_transaction_result(tx_hash)
                return tx_result
            except JSONRPCException as e:
                print(e.message)
                sleep(2)


class QueryHandler(object):
    def __init__(self, service, nid: int, address: str = EOA_ADDRESS):
        self._icon_service = service
        self._nid = nid
        self._from = address

    def call(self, method: str, params: dict):
        call = CallBuilder() \
            .from_(self._from) \
            .to(GOVERNANCE_ADDRESS) \
            .method(method) \
            .params(params) \
            .build()
        return self._icon_service.call(call)

    def get_tx_result(self, tx_hash: str):
        tx_result = self._icon_service.get_transaction_result(tx_hash)
        return tx_result


class GovernanceReader(object):
    def __init__(self, service, nid: int, address: str = EOA_ADDRESS):
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

    def print_info(self):
        print('[Governor]')
        print_response('Version', self.get_version())
        print_response('Revision', self.get_revision())

    def check_if_audit_enabled(self):
        service_config = self.get_service_config()
        if service_config['AUDIT'] == '0x1':
            return True
        else:
            return False

    def get_step_costs(self):
        return self._call(method="getStepCosts")

    def get_tx_result(self, tx_hash: str) -> dict:
        tx_result = self._icon_service.get_transaction_result(tx_hash)
        return tx_result


class GovernanceWriter(object):
    def __init__(self, service, nid: int, owner):
        self._icon_service = service
        self._owner = owner
        self._nid = nid

    def _call(self, method: str, params: dict, step_limit: int = 0x10000000) -> bytes:
        tx_handler = self._create_tx_handler()
        return tx_handler.invoke(
            owner=self._owner,
            to=GOVERNANCE_ADDRESS,
            limit=step_limit,
            method=method,
            params=params
        )

    def _create_tx_handler(self) -> TxHandler:
        return TxHandler(self._icon_service, self._nid)

    def update(self, score_path: str) -> bytes:
        """Update governance SCORE

        :return: tx_hash
        """
        content: bytes = gen_deploy_data_content(score_path)

        tx_handler = TxHandler(self._icon_service, self._nid)
        ret = tx_handler.update(self._owner, GOVERNANCE_ADDRESS, content, limit=0x70000000)

        return ret

    def accept_score(self, tx_hash: bytes) -> bytes:
        method = "acceptScore"
        params = {"txHash": tx_hash}

        return self._call(method, params)

    def set_revision(self, revision: int, name: str) -> bytes:
        """Set revision to governance SCORE

        :param revision:
        :param name:
        :return:
        """
        method = "setRevision"
        params = {"revision": revision, "name": name}

        return self._call(method, params)

    def set_step_cost(self, step_type: str, cost: int) -> bytes:
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


def create_reader_by_args(args) -> GovernanceReader:
    url: str = args.url
    nid: int = args.nid

    return create_reader(url, nid)


def create_reader(url: str, nid: int) -> GovernanceReader:
    icon_service = IconService(HTTPProvider(url))
    return GovernanceReader(icon_service, nid)


def create_writer_by_args(args) -> GovernanceWriter:
    url: str = args.url
    nid: int = args.nid
    keystore_path: str = args.keystore
    password: str = args.password

    if password is None:
        password = getpass.getpass("> Password: ")

    return create_writer(url, nid, keystore_path, password)


def create_writer(url: str, nid: int, keystore_path: str, password: str) -> GovernanceWriter:
    icon_service = IconService(HTTPProvider(url))

    owner_wallet = KeyWallet.load(keystore_path, password)
    print(f"ownerAddress: {owner_wallet.get_address()}")

    return GovernanceWriter(icon_service, nid, owner_wallet)
