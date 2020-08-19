# -*- coding: utf-8 -*-

import getpass
import json
import pprint
from typing import TYPE_CHECKING, Union, Optional, Any, Type
from urllib.parse import urlparse

from icon.data import str_to_object_by_type, RpcRequest
from icon.wallet import KeyWallet

from .constants import COLUMN, PREDEFINED_URLS

if TYPE_CHECKING:
    from urllib.parse import ParseResult


def hex_to_bytes(tx_hash: str) -> bytes:
    return bytes.fromhex(tx_hash[2:])


def print_title(title: str, column: int = COLUMN, sep: str = "="):
    sep_count: int = max(0, column - len(title) - 3)
    print(f"[{title}] {sep * sep_count}")


def print_dict(data: dict):
    converted = {}

    for key in data:
        value = data[key]
        if isinstance(value, bytes):
            value = f"0x{value.hex()}"

        converted[key] = value

    print(json.dumps(converted, indent=4))


def print_response(content: Union[bool, int, str, dict]):
    print_title("Response", COLUMN)

    if isinstance(content, dict):
        print_dict(content)
    else:
        print(content)

    print("")


def print_tx_result(tx_result: dict):
    print_title("Transaction Result")
    print_dict(tx_result)


def is_url_valid(url: str) -> bool:
    ps: "ParseResult" = urlparse(url)

    return ps.scheme in ("http", "https") and len(ps.netloc) > 0 and len(ps.path) > 0


def get_predefined_url(name: str) -> Optional[str]:
    if name not in PREDEFINED_URLS:
        return None

    return PREDEFINED_URLS[name][0]


def get_predefined_nid(name: str) -> int:
    item = PREDEFINED_URLS.get(name)
    return item[1] if item else -1


def resolve_url(url: str) -> str:
    predefined_url: str = get_predefined_url(url)

    if isinstance(predefined_url, str):
        return predefined_url

    if not is_url_valid(url):
        raise ValueError(f"Invalid url: {url}")

    return url


def resolve_nid(nid: int, url: str) -> int:
    if nid < 0:
        nid = get_predefined_nid(url)
        if nid < 0:
            ValueError("nid is required")

    return nid


def resolve_wallet(args) -> KeyWallet:
    path: str = args.keystore
    password: str = args.password

    if password is None:
        password = getpass.getpass("> Password: ")

    return KeyWallet.load(path, password)


def print_result(object_type: Optional[Type], result: Any):
    ret = str_to_object_by_type(object_type, result)
    pprint.pprint(ret)


def confirm_transaction(request: RpcRequest, yes: bool) -> bool:
    print_title("Request", COLUMN)
    print_dict(request.to_dict())
    print("")

    if not yes:
        ret: str = input("> Continue? [Y/n]")
        if ret == "n":
            return False

    return True
