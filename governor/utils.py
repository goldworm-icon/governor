# -*- coding: utf-8 -*-

import getpass
import json
from typing import TYPE_CHECKING, Optional, Any, Dict
from urllib.parse import urlparse

import icon
from icon.data import RpcRequest, TransactionResult, Address
from icon.provider import HTTPProvider
from icon.wallet import KeyWallet, LightWallet
from neotermcolor import colored

from .constants import COLUMN, PREDEFINED_URLS, PREDEFINED_ADDRESSES

if TYPE_CHECKING:
    from urllib.parse import ParseResult


def print_title(title: str, column: int = COLUMN, sep: str = "="):
    sep_count: int = max(0, column - len(title) - 3)
    print(f"[{title}] {sep * sep_count}")


def print_dict(data: Dict[str, str]):
    print(json.dumps(data, indent=4))


def print_tx_result(tx_result: TransactionResult):
    print_with_title("TransactionResult", tx_result)


def is_url_valid(url: str) -> bool:
    ps: ParseResult = urlparse(url)

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


def resolve_address(text: str) -> Address:
    if text.startswith("hx") or text.startswith("cx"):
        return Address.from_string(text)

    address: Address = PREDEFINED_ADDRESSES.get(text)
    if address is None:
        raise ValueError(f"Invalid address: {text}")

    return address


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


def print_with_title(title: str, data: Any):
    if isinstance(data, (dict, list)):
        data = json.dumps(data, indent=4)

    sep_count: int = max(0, 80 - len(title) - 3)
    title = f"[{title}] {'=' * sep_count}"
    title = colored(title, "green", attrs=["bold"])

    print(f"{title}\n{data}\n")


def print_arguments(data: Any):
    print_with_title("Arguments", data)


def print_request(data: Any):
    print_with_title("Request", data)


def print_response(data: Any):
    print_with_title("Response", data)


def print_result(data: Any):
    print_with_title("Result", data)


def confirm_transaction(request: RpcRequest, yes: bool) -> bool:
    print_request(request)
    if yes:
        return True

    ret: str = input("> Continue? [Y/n]")
    return ret.lower() != "n"


def get_address_from_args(args) -> Optional[Address]:
    if hasattr(args, "address") and isinstance(args.address, str):
        return Address.from_string(args.address)
    elif hasattr(args, "keystore") and isinstance(args.keystore, str):
        wallet = LightWallet.from_path(args.keystore)
        return wallet.address

    return None


def create_client(url: str) -> icon.Client:
    o = urlparse(url)
    return icon.Client(HTTPProvider(f"{o.scheme}://{o.netloc}", 3))
