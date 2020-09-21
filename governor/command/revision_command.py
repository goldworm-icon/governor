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

__all__ = ("RevisionCommand", "VersionCommand", "SetRevisionCommand")

from typing import Dict

from .command import Command
from ..score.governance import create_writer_by_args, create_reader_by_args
from ..utils import (
    print_result,
)


class RevisionCommand(Command):
    def __init__(self):
        self._name = "revision"

    @property
    def name(self) -> str:
        return self._name

    def init(self, sub_parser, common_parent_parser, invoke_parent_parser):
        desc = f"getRevision command of governance score"

        score_parser = sub_parser.add_parser(
            self._name, parents=[common_parent_parser], help=desc
        )

        score_parser.set_defaults(func=self._run)

    @classmethod
    def _run(cls, args) -> int:
        reader = create_reader_by_args(args)
        revision: Dict[str, str] = reader.get_revision()
        print_result(revision)

        return 0


class VersionCommand(Command):
    def __init__(self):
        self._name = "version"

    @property
    def name(self) -> str:
        return self._name

    def init(self, sub_parser, common_parent_parser, invoke_parent_parser):
        desc = f"getVersion command of governance score"

        score_parser = sub_parser.add_parser(
            self._name, parents=[common_parent_parser], help=desc
        )

        score_parser.set_defaults(func=self._run)

    @classmethod
    def _run(cls, args) -> int:
        reader = create_reader_by_args(args)
        version: str = reader.get_version()
        print_result(version)

        return 0


class SetRevisionCommand(Command):
    def __init__(self):
        self._name = "setRevision"

    @property
    def name(self) -> str:
        return self._name

    def init(self, sub_parser, common_parent_parser, invoke_parent_parser):
        desc = f"{self._name} command of governance score"

        score_parser = sub_parser.add_parser(
            self._name, parents=[common_parent_parser, invoke_parent_parser], help=desc
        )

        score_parser.add_argument(
            "revision", type=int, nargs="?", default=-1, help="revision ex) 3"
        )
        score_parser.add_argument(
            "name", type=str, nargs="?", default="", help="iconservice version ex) 1.2.3"
        )

        score_parser.set_defaults(func=self._run)

    @classmethod
    def _run(cls, args) -> bytes:
        revision: int = args.revision
        name: str = args.name

        writer = create_writer_by_args(args)
        return writer.set_revision(revision, name)
