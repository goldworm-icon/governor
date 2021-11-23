# -*- coding: utf-8 -*-
import argparse
import getpass
import json
import os
import re
from typing import TYPE_CHECKING, Optional, Any, Dict
from urllib.parse import urlparse

from neotermcolor import colored

from icon.data import RpcRequest, TransactionResult, Address
from icon.wallet import KeyWallet, LightWallet
from .constants import COLUMN, PREDEFINED_URLS, PREDEFINED_ADDRESSES

if TYPE_CHECKING:
    from urllib.parse import ParseResult

NUMBER_PATTERN = re.compile("[\d]+")
EXP_PATTERN = re.compile("[\d]+e[\d]+")


class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Address):
            return str(obj)
        return json.JSONEncoder.default(self, obj)


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
    password: str = get_password(args.password)
    return KeyWallet.load(path, password)


def get_password(password: Optional[str] = None) -> str:
    if password is None:
        password = getpass.getpass("> Password: ")
    return password


def print_with_title(title: str, data: Any):
    if isinstance(data, (dict, list)):
        data = json.dumps(data, indent=4, cls=CustomJSONEncoder)

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
        return resolve_address(args.address)
    elif hasattr(args, "keystore") and isinstance(args.keystore, str):
        wallet = LightWallet.from_path(args.keystore)
        return wallet.address

    return None


def get_coin_from_string(value: str) -> Optional[int]:
    m = NUMBER_PATTERN.fullmatch(value)
    if m:
        return int(m.group(), 10)

    return exp_to_int(value)


def exp_to_int(value: str) -> Optional[int]:
    m = EXP_PATTERN.fullmatch(value)
    if m is None:
        return None

    nums = value.split("e")
    return int(nums[0], 10) * 10 ** int(nums[1], 10)


def add_keystore_argument(parser: argparse.ArgumentParser, required: bool):
    parser.add_argument(
        "--keystore",
        "-k",
        type=str,
        default=os.environ.get("GOV_KEY_STORE", None),
        required=required,
        help="keystore file path"
    )


def add_password_argument(parser: argparse.ArgumentParser):
    parser.add_argument(
        "--password",
        "-p",
        type=str,
        required=False,
        default=os.environ.get("GOV_PASSWORD", None),
        help="keystore password",
    )
