# -*- coding: utf-8 -*-

from typing import Dict, Any, List, Tuple, Optional, Callable, Union

import icon
from icon.builder import CallBuilder, CallTransactionBuilder, Transaction
from icon.data import Address, SYSTEM_SCORE_ADDRESS
from icon.wallet import KeyWallet


class SystemScore(object):
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

    def claim_iscore(self, hooks: Dict[str, Callable] = None) -> Union[bytes, int]:
        tx: Transaction = self._create_call_tx("claimIScore")
        return self._client.send_transaction(tx, estimate=self._estimate, hooks=hooks)

    def get_delegation(self, address: Address, hooks: Dict[str, Callable] = None) -> Dict[str, Any]:
        method = "getDelegation"
        call_params = {"address": address}
        params = self._create_query_call(method, call_params)
        return self._client.call(params, hooks=hooks)

    def get_prep(self, address: Address, hooks: Dict[str, Callable] = None) -> Dict[str, str]:
        method = "getPRep"
        call_params = {"address": address}
        params = self._create_query_call(method, call_params)
        return self._client.call(params, hooks=hooks)

    def get_preps(self, start: int, end: int, height: int, hooks: Dict[str, Callable] = None) -> Dict[str, Any]:
        method = "getPReps"

        call_params = {}
        if start > 0:
            call_params["startRanking"] = start
        if end > 0:
            call_params["endRanking"] = end

        params = self._create_query_call(method, call_params)
        if height > -1:
            params["height"] = hex(height)
        return self._client.call(params, hooks=hooks)

    def get_main_preps(self, height: int, hooks: Dict[str, Callable] = None) -> Dict[str, Any]:
        method = "getMainPReps"
        params = self._create_query_call(method, {})
        if height > -1:
            params["height"] = hex(height)
        return self._client.call(params, hooks=hooks)

    def get_sub_preps(self, hooks: Dict[str, Callable] = None) -> Dict[str, Any]:
        method = "getSubPReps"
        params = self._create_query_call(method, {})
        return self._client.call(params, hooks=hooks)

    def get_prep_stats(self, hooks: Dict[str, Callable] = None) -> Dict[str, Any]:
        method = "getPRepStats"
        call_params = {}

        params = self._create_query_call(method, call_params)
        return self._client.call(params, hooks=hooks)

    def get_stake(self, address: Address, hooks: Dict[str, Callable] = None) -> Dict[str, str]:
        method = "getStake"
        call_params = {"address": address}
        params = self._create_query_call(method, call_params)
        return self._client.call(params, hooks=hooks)

    def set_delegation(
        self,
        delegations: List[Tuple[Address, int]],
        hooks: Dict[str, Callable] = None
    ) -> Union[bytes, int]:
        _delegations = []
        call_params = {"delegations": _delegations}

        for address, value in delegations:
            _delegations.append({"address": address, "value": value})

        tx = self._create_call_tx("setDelegation", call_params)
        return self._client.send_transaction(tx, estimate=self._estimate, hooks=hooks)

    def set_stake(self, stake: int, hooks: Dict[str, Callable] = None) -> Union[bytes, int]:
        call_params = {"value": stake}
        tx = self._create_call_tx("setStake", call_params)
        return self._client.send_transaction(tx, estimate=self._estimate, hooks=hooks)

    def query_iscore(self, address: Address, hooks: Dict[str, Callable] = None) -> Dict[str, str]:
        method = "queryIScore"
        call_params = {"address": address}
        params = self._create_query_call(method, call_params)
        return self._client.call(params, hooks=hooks)

    def get_bonder_list(self, address: Address, hooks: Dict[str, Callable] = None) -> Dict[str, str]:
        method = "getBonderList"
        call_params = {"address": address}
        params = self._create_query_call(method, call_params)
        return self._client.call(params, hooks=hooks)

    def set_bonder_list(
            self, bonder_list: List[Address], hooks: Dict[str, Callable] = None, **kwargs
    ) -> Union[bytes, int]:
        call_params = {"bonderList": bonder_list}
        tx = self._create_call_tx("setBonderList", call_params, hooks=hooks)
        return self._client.send_transaction(tx, hooks=hooks)

    def get_bond(self, address: Address, hooks: Dict[str, Callable] = None) -> Dict[str, str]:
        method = "getBond"
        call_params = {"address": address}
        params = self._create_query_call(method, call_params)
        return self._client.call(params, hooks=hooks)

    def get_iiss_info(self, hooks: Dict[str, Callable] = None) -> Dict[str, str]:
        method = "getIISSInfo"
        params = self._create_query_call(method, None)
        return self._client.call(params, hooks=hooks)

    def get_revision(self, hooks: Dict[str, Callable] = None) -> int:
        method = "getRevision"
        params = self._create_query_call(method, None)
        hex_revision: str = self._client.call(params, hooks=hooks)
        return int(hex_revision, base=16)

    def get_prep_term(self, hooks: Dict[str, Callable] = None) -> Dict[str, str]:
        method = "getPRepTerm"
        params = self._create_query_call(method, None)
        return self._client.call(params, hooks=hooks)

    def get_score_owner(self, score: Address, hooks: Dict[str, Callable] = None) -> Address:
        call_params = {"score": score}
        params = self._create_query_call("getScoreOwner", call_params)
        return Address.from_string(self._client.call(params, hooks=hooks))

    def get_network_info(self, hooks: Dict[str, Callable] = None) -> Dict[str, str]:
        method = "getNetworkInfo"
        params = self._create_query_call(method, None)
        return self._client.call(params, hooks=hooks)

    def _create_call_tx(self, method: str, params: Dict[str, Any] = None, **kwargs) -> Transaction:
        builder = (
            CallTransactionBuilder()
            .nid(self._nid)
            .from_(self._owner.address)
            .to(SYSTEM_SCORE_ADDRESS)
            .call_data(method, params)
        )

        step_limit: int = self._step_limit
        print(f"step_limit: {step_limit}")
        if step_limit <= 0:
            # Do not add stepLimit to tx if you want to estimate the step of a tx
            tx: Transaction = builder.build()
            step_limit = self._client.estimate_step(tx, **kwargs)

        builder.step_limit(step_limit)
        tx: Transaction = builder.build()
        tx.sign(self._owner.private_key)

        return tx

    @classmethod
    def _create_query_call(
        cls, method: str, params: Optional[Dict[str, Any]]
    ) -> Dict[str, str]:
        params: Dict[str, str] = (
            CallBuilder()
            .to(SYSTEM_SCORE_ADDRESS)
            .call_data(method, params=params)
            .build()
        )

        return params
