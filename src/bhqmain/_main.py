# SPDX-FileCopyrightText: 2020-2024 Ivan Perevala <ivan95perevala@gmail.com>
#
# SPDX-License-Identifier: GPL-3.0-or-later

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, ClassVar, Type, TypeVar, Generic, Mapping
from enum import auto, IntEnum

if TYPE_CHECKING:
    from bpy.types import Context

__all__ = (
    "MainChunk",
    "InvokeState",
)

log = logging.getLogger(__name__)


_MainChunkType = TypeVar("_MainChunkType", bound="MainChunk")


class InvokeState(IntEnum):
    NOT_CALLED = auto()
    SUCCESSFUL = auto()
    FAILED = auto()


class MainChunk(Generic[_MainChunkType]):
    # NOTE: Class variables default value affects unit tests, so please, update them alongside.
    _init_lock: ClassVar[bool] = True

    chunks: Mapping[str, Type[MainChunk[_MainChunkType]]] = {}

    _invoke_state: InvokeState
    _instance: None | _MainChunkType = None

    main: _MainChunkType

    @classmethod
    def get_instance(cls) -> None | _MainChunkType:
        if cls._instance and cls._instance._invoke_state == InvokeState.SUCCESSFUL:
            return cls._instance

    @classmethod
    def create(cls) -> _MainChunkType:
        if cls._instance is None:
            cls._init_lock = False
            cls._instance = cls(None)
            cls._init_lock = True
        return cls._instance

    def __init__(self, main: None | MainChunk[_MainChunkType]):
        cls = self.__class__

        self.main = main

        if __debug__:
            if cls is _MainChunkType:
                raise TypeError(f"{cls.__name__} should not be used directly")

            if cls._instance is not None:
                raise AssertionError(f"{cls.__name__} is a singleton class")

            if cls._init_lock:
                raise AssertionError(f"{cls.__name__} can only be created using the create method")

        self._invoke_state = InvokeState.NOT_CALLED

        for attr, chunk_cls in self.chunks.items():
            chunk_cls._init_lock = False
            if main:
                chunk = chunk_cls(main)
            else:
                chunk = chunk_cls(self)
            chunk_cls._init_lock = True
            setattr(self, attr, chunk)

        cls._instance = self

    def invoke(self, context: Context) -> InvokeState:
        """
        Invoke the main chunks in order and manage their state.

        - Checks if the invoke method has already been called.
        - Iterates through each chunk, invoking them in sequence.
        - If any chunk fails to invoke, it cancels all previously invoked chunks.
        - Sets the invoke state accordingly.

        :param context: The context in which the invocation occurs.
        :type context: Context

        :returns: The state after invocation, either SUCCESSFUL or FAILED.
        :rtype: InvokeState
        """

        cls = self.__class__
        if not cls.chunks:
            return InvokeState.SUCCESSFUL

        if self._invoke_state != InvokeState.NOT_CALLED:
            return self._invoke_state

        chunks_invocation_began = []

        for attr in self.chunks.keys():
            chunk: MainChunk = getattr(self, attr)
            chunks_invocation_began.append(chunk)

            if chunk.invoke(context) != InvokeState.SUCCESSFUL:
                log.info(f"Failed to invoke {chunk.__class__.__name__}, cancelling")
                break
        else:
            self._invoke_state = InvokeState.SUCCESSFUL
            return self._invoke_state

        for chunk in reversed(chunks_invocation_began):
            if not chunk.cancel(context):
                log.warning(f"Failed to cancel {chunk.__class__.__name__} invocation after failure")

        self._invoke_state = InvokeState.FAILED
        return self._invoke_state

    def cancel(self, context: Context) -> InvokeState:
        """
        Cancels the execution of all chunks in reverse order.
        This method iterates over all chunks defined in the class in reverse order
        and attempts to cancel each one. If any chunk fails to cancel, a warning
        is logged and the method returns False. If all chunks are successfully
        canceled, the method returns True.

        :param context: The context in which the cancellation is being performed.
        :type context: Context
        :returns: True if all chunks are successfully canceled, False otherwise.
        :rtype: bool
        :returns: True if all chunks are successfully canceled, False otherwise.
        :rtype: bool
        """

        cls = self.__class__

        if not cls.chunks:
            return InvokeState.SUCCESSFUL

        if self._invoke_state != InvokeState.SUCCESSFUL:
            return self._invoke_state

        for attr in reversed(cls.chunks.keys()):
            chunk: MainChunk = getattr(self, attr)
            if not chunk.cancel(context):
                log.warning(f"Failed to cancel {chunk.__class__.__name__} chunk")
                return InvokeState.FAILED

        cls._instance = None
        return InvokeState.SUCCESSFUL
