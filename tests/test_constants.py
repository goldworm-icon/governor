# -*- coding: utf-8 -*-

import pytest

from governor.utils import get_predefined_url


@pytest.mark.parametrize(
    "url", ("mainnet", "testnet", "bicon", "zicon", "qanet", "localnet")
)
def test_get_predefined_url(url):
    ret = get_predefined_url(url)
    assert isinstance(ret, str)
    assert ret != url
