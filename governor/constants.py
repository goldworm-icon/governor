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
    AddressPrefix,
    BURN_ADDRESS,
    GOVERNANCE_SCORE_ADDRESS,
    SYSTEM_SCORE_ADDRESS,
    TREASURY_ADDRESS,
)

EOA_ADDRESS = Address.from_string("hx1234567890123456789012345678901234567890")

COLUMN = 80

PREDEFINED_URLS = {
    "berlin": ("https://berlin.net.solidwallet.io/api/v3", 7),
    "gochain": ("http://localhost:9082/api/v3", 3),
    "lisbon": ("https://lisbon.net.solidwallet.io/api/v3", 2),
    "localnet": ("http://127.0.0.1:9000/api/v3", 3),
    "mainnet": ("https://ctz.solidwallet.io/api/v3", 1),
    "sejong": ("https://sejong.net.solidwallet.io/api/v3", 0x53),
    "testnet": ("https://test-ctz.solidwallet.io/api/v3", 2),
    "qanet": ("https://eunsoo.net.solidwallet.io/api/v3", 80),
    "havah": ("https://ctz.havah.io/api/v3", 256),
    "vega": ("https://ctz.vega.havah.io/api/v3", 257),
    "deneb": ("https://ctz.dev.havah.io/api/v3", 272),
}

PREDEFINED_ADDRESSES = {
    "system": SYSTEM_SCORE_ADDRESS,
    "sys": SYSTEM_SCORE_ADDRESS,
    "governance": GOVERNANCE_SCORE_ADDRESS,
    "gov": GOVERNANCE_SCORE_ADDRESS,
    "treasury": TREASURY_ADDRESS,
    "burn": BURN_ADDRESS,
    "cpft": Address.from_string("cxdca1178010b5368aea929ad5c06abee64b91acc2"),
    "cpst": Address.from_string("cxd965531d1cce5daad1d1d3ee1efb39ce68f442fc"),
    "cps": Address.from_string("cx9f4ab72f854d3ccdc59aa6f2c3e2215dd62e879f"),
    "zero": Address.from_int(AddressPrefix.EOA, 0)
}

DEFAULT_URL, DEFAULT_NID = PREDEFINED_URLS["mainnet"]
