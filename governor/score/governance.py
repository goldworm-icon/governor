# -*- coding: utf-8 -*-

import logging
from typing import Dict, Any, Optional, Union

import icon
from icon.builder import (
    CallBuilder,
    CallTransactionBuilder,
    Transaction,
    Key
)
from icon.data import (
    Address,
    GOVERNANCE_SCORE_ADDRESS,
)
from icon.wallet import KeyWallet


class GovernanceScore(object):
    def __init__(
        self,
        client: icon.Client,
        owner: KeyWallet = None,
        nid: int = 0,
        step_limit: int = 0,
        estimate: bool = False,
    ):
        self._client = client
        self._owner = owner
        self._nid = nid
        self._step_limit = step_limit
        self._estimate = estimate
        self._score_address: Address = GOVERNANCE_SCORE_ADDRESS

    def _create_query_call(
        self, method: str, params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, str]:
        params: Dict[str, str] = (
            CallBuilder()
            .to(self._score_address)
            .call_data(method, params=params)
            .build()
        )

        return params

    def _create_call_tx(
            self, method: str, params: Dict[str, Any] = None, **kwargs,
    ) -> Transaction:
        step_limit: int = kwargs.get("step_limit", self._step_limit)

        builder = (
            CallTransactionBuilder()
            .nid(self._nid)
            .from_(self._owner.address)
            .to(self._score_address)
            .call_data(method, params)
        )

        if step_limit <= 0:
            # Do not add stepLimit to tx if you want to estimate the step of a tx
            tx: Transaction = builder.build()
            step_limit = self._client.estimate_step(tx, **kwargs)

        builder.step_limit(step_limit)
        tx: Transaction = builder.build()
        tx.sign(self._owner.private_key)

        return tx

    def _estimate_step(self, tx: icon.builder.Transaction, **kwargs) -> int:
        _builder = icon.builder.GenericBuilder(tx.to_dict())
        _builder.remove(Key.SIGNATURE)
        _builder.remove(Key.STEP_LIMIT)
        return self._client.estimate_step(tx, **kwargs)

    def get_version(self, **kwargs) -> str:
        method = "getVersion"
        params: Dict[str, str] = self._create_query_call(method)
        return self._client.call(params, **kwargs)

    def get_revision(self, **kwargs) -> Dict[str, str]:
        method = "getRevision"
        params: Dict[str, str] = self._create_query_call(method)
        return self._client.call(params, **kwargs)

    def get_service_config(self, **kwargs) -> Dict[str, str]:
        method = "getServiceConfig"
        params: Dict[str, str] = self._create_query_call(method)
        return self._client.call(params, **kwargs)

    def get_score_status(self, address: Address, **kwargs) -> Dict[str, str]:
        method = "getScoreStatus"
        call_params = {"address": address}
        params: Dict[str, str] = self._create_query_call(method, call_params)
        return self._client.call(params, **kwargs)

    def get_step_price(self, **kwargs) -> int:
        method = "getStepPrice"
        params: Dict[str, str] = self._create_query_call(method)
        ret: str = self._client.call(params, **kwargs)
        return int(ret, base=0)

    def get_step_costs(self, **kwargs) -> Dict[str, str]:
        method = "getStepCosts"
        params: Dict[str, str] = self._create_query_call(method)
        return self._client.call(params, **kwargs)

    def get_max_step_limit(self, context_type: str, **kwargs) -> int:
        """
        :param context_type: "invoke" or "query"
        :return: maximum step limit
        """
        method = "getMaxStepLimit"
        call_params = {"contextType": context_type}
        params: Dict[str, str] = self._create_query_call(method, call_params)
        ret: str = self._client.call(params, **kwargs)
        return int(ret, base=0)

    def is_in_score_black_list(self, address: Address, **kwargs) -> bool:
        method = "isInScoreBlackList"
        call_params = {"address": address}
        params: Dict[str, str] = self._create_query_call(method, call_params)
        ret: str = self._client.call(params, **kwargs)
        return bool(int(ret, base=0))

    def is_in_import_white_list(self, import_stmt: str, **kwargs) -> bool:
        method = "isInImportWhiteList"
        call_params = {"importStmt": import_stmt}
        params: Dict[str, str] = self._create_query_call(method, call_params)
        ret: str = self._client.call(params, **kwargs)
        return bool(int(ret, base=0))

    def is_auditor(self, address: Address, **kwargs) -> bool:
        method = "isAuditor"
        call_params = {"importStmt": import_stmt}
        params: Dict[str, str] = self._create_query_call(method, call_params)
        ret: str = self._client.call(params, **kwargs)
        return bool(int(ret, base=0))

    # The following is invoke functions

    def accept_score(self, tx_hash: bytes, **kwargs) -> Union[bytes, int]:
        method = "acceptScore"
        call_params = {"txHash": tx_hash}
        tx: Transaction = self._create_call_tx(method, call_params, **kwargs)
        return self._client.send_transaction(tx, **kwargs)

    def reject_score(self, tx_hash: bytes, reason: str, **kwargs) -> Union[bytes, int]:
        method = "rejectScore"
        call_params = {"txHash": tx_hash, "reason": reason}
        tx: Transaction = self._create_call_tx(method, call_params, **kwargs)
        return self._client.send_transaction(tx, **kwargs)

    def add_auditor(self, address: Address, **kwargs) -> Union[bytes, int]:
        method = "addAuditor"
        call_params = {"address": address}
        tx: Transaction = self._create_call_tx(method, call_params, **kwargs)
        return self._client.send_transaction(tx, **kwargs)

    def remove_auditor(self, address: Address, **kwargs) -> Union[bytes, int]:
        method = "removeAuditor"
        call_params = {"address": address}
        tx: Transaction = self._create_call_tx(method, call_params, **kwargs)
        return self._client.send_transaction(tx, **kwargs)

    def set_revision(self, revision: int, name: str, **kwargs) -> Union[bytes, int]:
        """Set revision to governance SCORE

        :param revision:
        :param name:
        :return:
        """
        method = "setRevision"
        call_params = {"code": revision, "name": name}
        tx: Transaction = self._create_call_tx(method, call_params, **kwargs)
        return self._client.send_transaction(tx, **kwargs)

    def set_step_price(self, step_price: int, **kwargs) -> bytes:
        logging.debug(f"set_step_price() start: step_price={step_price}")

        method = "setStepPrice"
        call_params = {"stepPrice": step_price}
        tx: Transaction = self._create_call_tx(method, call_params, **kwargs)

        ret = self._client.send_transaction(tx, **kwargs)

        logging.debug(f"set_step_price() end")
        return ret

    def set_step_cost(self, step_type: str, cost: int, **kwargs) -> Union[bytes, int]:
        """
        URL: https://github.com/icon-project/governance#setstepcost

        :param step_type:
        :param cost:
        :return:
        """
        step_types = {
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
        }

        if step_type not in step_types:
            raise ValueError(f"Invalid stepType: {step_type}")

        method = "setStepCost"
        call_params = {"stepType": step_type, "cost": cost}
        tx: Transaction = self._create_call_tx(method, call_params, **kwargs)
        return self._client.send_transaction(tx, **kwargs)

    def set_max_step_limit(self, context_type: str, value: int, **kwargs) -> Union[bytes, int]:
        context_types = {"invoke", "query"}

        if context_type not in context_types:
            raise ValueError(f"Invalid contextType: {context_type}")

        method = "setMaxStepLimit"
        call_params = {"contextType": context_type, "value": value}
        tx: Transaction = self._create_call_tx(method, call_params, **kwargs)
        return self._client.send_transaction(tx, **kwargs)

    def add_deployer(self, address: Address, **kwargs) -> Union[bytes, int]:
        method = "addDeployer"
        call_params = {"address": address}
        tx: Transaction = self._create_call_tx(method, call_params, **kwargs)
        return self._client.send_transaction(tx, **kwargs)

    def remove_deployer(self, address: Address, **kwargs) -> Union[bytes, int]:
        method = "removeDeployer"
        call_params = {"address": address}
        tx: Transaction = self._create_call_tx(method, call_params, **kwargs)
        return self._client.send_transaction(tx, **kwargs)

    def add_to_score_black_list(self, address: Address, **kwargs) -> Union[bytes, int]:
        method = "addToScoreBlackList"
        call_params = {"address": address}
        tx: Transaction = self._create_call_tx(method, call_params, **kwargs)
        return self._client.send_transaction(tx, **kwargs)

    def remove_from_score_black_list(self, address: Address, **kwargs) -> Union[bytes, int]:
        method = "removeFromScoreBlackList"
        call_params = {"address": address}
        tx: Transaction = self._create_call_tx(method, call_params, **kwargs)
        return self._client.send_transaction(tx, **kwargs)

    def add_import_white_list(self, import_stmt: str, **kwargs) -> Union[bytes, int]:
        method = "addImportWhiteList"
        call_params = {"importStmt": import_stmt}
        tx: Transaction = self._create_call_tx(method, call_params, **kwargs)
        return self._client.send_transaction(tx, **kwargs)

    def remove_import_white_list(self, import_stmt: str, **kwargs) -> Union[bytes, int]:
        method = "removeImportWhiteList"
        call_params = {"importStmt": import_stmt}
        tx: Transaction = self._create_call_tx(method, call_params, **kwargs)
        return self._client.send_transaction(tx, **kwargs)

    def update_service_config(self, service_flag: int, **kwargs) -> Union[bytes, int]:
        method = "updateServiceConfig"
        call_params = {"serviceFlag": service_flag}
        tx: Transaction = self._create_call_tx(method, call_params, **kwargs)
        return self._client.send_transaction(tx, **kwargs)
