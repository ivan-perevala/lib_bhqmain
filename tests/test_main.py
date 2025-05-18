# SPDX-FileCopyrightText: 2020-2024 Ivan Perevala <ivan95perevala@gmail.com>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import pytest

import bhqmain4 as bhqmain

from . import tested_classes as clss


@pytest.fixture(autouse=True)
def reset():
    # NOTE: Reset the Main class to its initial state before each test.
    for cls in clss.TEST_CLASSES:
        cls._instance = None
        cls._init_lock = True


@pytest.fixture
def main_instance(reset):
    return clss.TestMain.create()


def test_init_raises():
    # Test that the Main class cannot be instantiated directly.
    with pytest.raises(AssertionError):
        clss.TestMain(None)


def test_create(main_instance):
    # Test that the Main class can be created.
    assert isinstance(main_instance(), clss.TestMain)

    # Test that instance was not invoked
    assert main_instance()._invoke_state == bhqmain.InvokeState._NOT_CALLED

    a = main_instance()

    # Test that chunk instances were created
    assert isinstance(main_instance().first_main_chunk, clss.FirstTestMainChunk)
    assert isinstance(main_instance().second_main_chunk, clss.SecondTestMainChunk)

    # Test that check value of chunk was not changed
    assert main_instance().first_main_chunk.check_value is False


def test_invoke_successfull(main_instance):
    context = clss.Context()

    # Check that with default context invocation would be successful and test value would be set to True
    assert main_instance().invoke(context) == bhqmain.InvokeState.SUCCESSFUL
    assert main_instance().first_main_chunk.check_value is True

    # Now manually set check value back to False ...
    main_instance().first_main_chunk.check_value = False

    # ... To test if all next calls to invoke method would return successful flag but check value would remain
    # the same - to check if there is no multiple invocation done.
    assert main_instance().invoke(context) == bhqmain.InvokeState.SUCCESSFUL
    assert main_instance().first_main_chunk.check_value is False


@pytest.fixture(scope="function", params=[1, 2, 3])
def invoke_fail_context(request) -> clss.Context:
    context = clss.Context()
    context.test_number_should_fail_invoke = request.param
    return context


def test_invoke_fails(reset, invoke_fail_context, main_instance):
    # Check that invocation was failed
    assert main_instance().invoke(invoke_fail_context) is bhqmain.InvokeState.FAILED

    # All check_value's must be set to False at this point because that changes should be reversed by cancelling them
    # in reverse order
    assert main_instance().first_main_chunk.check_value is False
    assert main_instance().second_main_chunk.check_value is False
    assert main_instance().third_main_chunk.check_value is False


@pytest.fixture(scope="function", params=[1, 2, 3])
def cancel_fail_context(request) -> clss.Context:
    context = clss.Context()
    context.test_number_should_fail_cancel = request.param
    return context


def test_cancel_fails(reset, cancel_fail_context, main_instance):
    # Check that invocation was done
    assert main_instance().invoke(cancel_fail_context) is bhqmain.InvokeState.SUCCESSFUL

    # Check that cancel was failed
    assert main_instance().cancel(cancel_fail_context) is bhqmain.InvokeState.FAILED

    # Check that at least one chunk check_value is set to True, because cancel method cant revert all changes
    is_one_chunk_checked = False
    for chunk in (main_instance().first_main_chunk, main_instance().second_main_chunk, main_instance().third_main_chunk):
        if chunk.check_value is True:
            is_one_chunk_checked = True

    assert is_one_chunk_checked is True
