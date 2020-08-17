# -*- coding: utf-8 -*-

from typing import Dict, Any, List, Tuple, Optional

import icon


class SystemScore(object):
    def __init__(
        self,
        client: icon.Client,
        owner: icon.KeyWallet,
        nid: int,
        step_limit: int,
        estimate: bool
    ):
        self._client = client
        self._owner = owner
        self._nid = nid
        self._step_limit = step_limit
        self._estimate = estimate

    def claim_iscore(self) -> bytes:
        pass

    def get_delegation(self, address: icon.Address) -> Dict[str, Any]:
        method = "getDelegation"
        call_params = {"address": address}
        params = self._create_query_call(method, call_params)
        return self._client.call(params)

    def get_prep(self, address: icon.Address) -> Dict[str, str]:
        method = "getPRep"
        call_params = {"address": address}
        params = self._create_query_call(method, call_params)
        return self._client.call(params)

    def get_preps(self, start: int, end: int) -> Dict[str, Any]:
        method = "getPRep"

        call_params = {}
        if start > 0:
            call_params["startRanking"] = start
        if end > 0:
            call_params["endRanking"] = end

        params = self._create_query_call(method, call_params)
        return self._client.call(params)

    def get_stake(self, address: icon.Address) -> Dict[str, str]:
        method = "getStake"
        call_params = {"address": address}
        params = self._create_query_call(method, call_params)
        return self._client.call(params)

    def set_delegation(self, delegations: List[Tuple[icon.Address, int]]) -> bytes:
        pass

    def set_stake(self, stake: int) -> bytes:
        pass

    def query_iscore(self, address: icon.Address) -> Dict[str, str]:
        method = "queryIScore"
        call_params = {"address": address}
        params = self._create_query_call(method, call_params)
        return self._client.call(params)

    def _create_call_tx(
        self, method: str, params: Dict[str, Any]
    ) -> icon.builder.Transaction:
        return (
            icon.CallTransactionBuilder()
            .nid(self._nid)
            .from_(self._owner.address)
            .to(icon.SYSTEM_SCORE_ADDRESS)
            .step_limit(self._step_limit)
            .call_data(method, params)
            .build()
        )

    @classmethod
    def _create_query_call(
        cls, method: str, params: Optional[Dict[str, Any]]
    ) -> Dict[str, str]:
        params: Dict[str, str] = (
            icon.CallBuilder()
                .to(icon.SYSTEM_SCORE_ADDRESS)
                .call_data(method, params=params)
                .build()
        )

        return params
