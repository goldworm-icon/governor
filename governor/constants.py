# -*- coding: utf-8 -*-

# Copyright 2019 ICON Foundation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from icon.data.address import (
    Address,
    SYSTEM_SCORE_ADDRESS,
    GOVERNANCE_SCORE_ADDRESS,
    TREASURY_ADDRESS,
)


EOA_ADDRESS = Address.from_string("hx1234567890123456789012345678901234567890")

DEFAULT_URL = "http://127.0.0.1:9000/api/v3"
DEFAULT_NID = 3

COLUMN = 80

PREDEFINED_URLS = {
    "bicon": ("https://bicon.net.solidwallet.io/api/v3", 3),
    "flower": ("http://15.164.158.156:9000/api/v3", 0x50),
    "gochain": ("http://localhost:9080/api/v3", 7),
    "hannam": ("https://hannam.net.solidwallet.io/api/v3", 3),
    "lisbon": ("https://lisbon.solidwallet.io/api/v3", 3),
    "localnet": (DEFAULT_URL, DEFAULT_NID),
    "mainnet": ("https://ctz.solidwallet.io/api/v3", 1),
    "sejong": ("https://sejong.net.solidwallet.io/api/v3", 0x53),
    "testnet": ("https://test-ctz.solidwallet.io/api/v3", 2),
    "qanet": ("https://eunsoo.net.solidwallet.io/api/v3", 80),
    "zicon": ("https://zicon.net.solidwallet.io/api/v3", 1),
}

PREDEFINED_ADDRESSES = {
    "system": SYSTEM_SCORE_ADDRESS,
    "sys": SYSTEM_SCORE_ADDRESS,
    "governance": GOVERNANCE_SCORE_ADDRESS,
    "gov": GOVERNANCE_SCORE_ADDRESS,
    "treasury": TREASURY_ADDRESS,
    "cpft": Address.from_string("cxdca1178010b5368aea929ad5c06abee64b91acc2"),
    "cpst": Address.from_string("cxd965531d1cce5daad1d1d3ee1efb39ce68f442fc"),
    "cps": Address.from_string("cx9f4ab72f854d3ccdc59aa6f2c3e2215dd62e879f"),
}
