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

import getpass

from iconsdk.icon_service import IconService
from iconsdk.providers.http_provider import HTTPProvider
from iconsdk.wallet.wallet import KeyWallet

from .governor import Governor


def create_governor(url: str, nid, keystore_path: str, password: str) -> Governor:
    if password is None:
        password = getpass.getpass("Password: ")

    icon_service = IconService(HTTPProvider(url))
    owner_wallet = KeyWallet.load(keystore_path, password)
    print(f"ownerAddress: {owner_wallet.get_address()}")

    return Governor(icon_service, owner_wallet, nid)
