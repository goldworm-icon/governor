# -*- coding: utf-8 -*-
# Copyright 2020 ICON Foundation
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

import os
import unittest

from governor import __version__


class TestVersion(unittest.TestCase):
    def test_version(self):
        here = os.path.abspath(os.path.dirname(__file__))
        path = os.path.join(here, "../governor/__version__.py")

        about = {}
        with open(path, "r") as f:
            exec(f.read(), about)

        expected = {
            "__title__": __version__.__title__,
            "__version__": __version__.__version__,
            "__author__": __version__.__author__,
            "__author_email__": __version__.__author_email__,
            "__url__": __version__.__url__
        }

        for key in expected:
            value = about[key]
            assert isinstance(value, str)
            assert value == expected[key]
