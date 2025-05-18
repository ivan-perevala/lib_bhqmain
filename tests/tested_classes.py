# SPDX-FileCopyrightText: 2020-2024 Ivan Perevala <ivan95perevala@gmail.com>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import bhqmain4 as bhqmain


class Context:
    __test__ = False

    test_number_should_fail_invoke: int
    test_number_should_fail_cancel: int

    def __init__(self):
        self.test_number_should_fail_invoke = -1
        self.test_number_should_fail_cancel = -1


def methods_helper(index: int):
    def _invoke_wrapper(self, context: Context) -> bhqmain.InvokeState:
        self.check_value = True
        if context.test_number_should_fail_invoke == index:
            return bhqmain.InvokeState.FAILED
        return bhqmain.InvokeState.SUCCESSFUL

    def _cancel_wrapper(self, context: Context) -> bhqmain.InvokeState:
        if context.test_number_should_fail_cancel == index:
            return bhqmain.InvokeState.FAILED
        self.check_value = False
        return bhqmain.InvokeState.SUCCESSFUL

    return _invoke_wrapper, _cancel_wrapper


class _TestMainChunkBase(bhqmain.MainChunk["TestMain", "Context"]):
    __test__ = False

    check_value: bool

    def __init__(self, main):
        super().__init__(main)
        self.check_value = False


class FirstTestMainChunk(_TestMainChunkBase):
    __test__ = False
    invoke, cancel = methods_helper(index=1)


class SecondTestMainChunk(_TestMainChunkBase):
    __test__ = False
    invoke, cancel = methods_helper(index=2)


class ThirdTestMainChunk(_TestMainChunkBase):
    __test__ = False
    invoke, cancel = methods_helper(index=3)


class TestMain(bhqmain.MainChunk["TestMain", "Context"]):
    __test__ = False

    first_main_chunk: FirstTestMainChunk
    second_main_chunk: SecondTestMainChunk
    third_main_chunk: ThirdTestMainChunk

    chunks = {
        "first_main_chunk": FirstTestMainChunk,
        "second_main_chunk": SecondTestMainChunk,
        "third_main_chunk": ThirdTestMainChunk,
    }


TEST_CLASSES = (
    TestMain,
    FirstTestMainChunk,
    SecondTestMainChunk,
    ThirdTestMainChunk
)
