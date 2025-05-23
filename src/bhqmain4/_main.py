# SPDX-FileCopyrightText: 2020-2025 Ivan Perevala <ivan95perevala@gmail.com>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import typing
import weakref
import logging
from typing import ClassVar, Type, TypeVar, Generic, Mapping
from enum import auto, IntEnum


__all__ = (
    "MainChunk",
    "MainChunkType",
    "ContextType",
    "InvokeState",
)

log = logging.getLogger(__name__)
_dbg = log.debug
_warn = log.warning


class InvokeState(IntEnum):
    """Initialization state. Returned by :meth:`MainChunk.invoke` and :meth:`MainChunk.cancel` methods.
    """

    _NOT_CALLED = auto()
    "Method was not called yet. Currently internal use only."

    SUCCESSFUL = auto()
    "Action was successful."

    FAILED = auto()
    "Action failed."


MainChunkType = TypeVar("MainChunkType", bound="MainChunk")
"Type variable used for :class:`MainChunk` instantination."

ContextType = TypeVar("ContextType")
"Type variable used for :class:`MainChunk` context."


class MainChunk(Generic[MainChunkType, ContextType]):
    """Generic base class designed to manage hierarchical chunks of functionality. 
    It provides mechanisms for creating, invoking, and canceling chunks, ensuring proper 
    state management and singleton behavior.

    :param Generic: Generic type representing the main chunk type.
    :type Generic: Generic[MainChunkType, ContextType]
    :cvar chunks: Chunks mapping, where keys are field names and values are other chunks.
    :type chunks: Mapping[str, Type[MainChunk[MainChunkType, ContextType]]]
    :raises TypeError: If the class is used directly instead of being subclassed.
    :raises AssertionError: If the class is instantiated without using the `create` method or if multiple instances
     are attempted to be created (should not happen).
    """

    # NOTE: Class variables default value affects unit tests, so please, update them alongside.
    _init_lock: ClassVar[bool] = True

    chunks: Mapping[str, Type[MainChunk[MainChunkType, ContextType]]] = {}
    
    _invoke_state: InvokeState
    _instance: None | MainChunkType = None

    main: MainChunkType

    @classmethod
    def _reset_variables(cls):
        cls._init_lock = True
        cls._instance = None

    @classmethod
    def get_instance(cls) -> None | weakref.ReferenceType[MainChunkType]:
        """Returns a weak reference to the singleton instance of the chunk. If the instance is not created or is in a
        failed state, it returns None. This method is useful for checking the current state of the chunk
        without creating a strong reference to it.        

        :return: Weak reference to the singleton instance of the chunk.
        :rtype: None | weakref.ReferenceType[MainChunkType]
        """
        if cls._instance and cls._instance._invoke_state == InvokeState.SUCCESSFUL:
            return weakref.ref(cls._instance)

    @classmethod
    def create(cls) -> weakref.ReferenceType[MainChunkType]:
        """Creates chunk instance. If instance already created, does nothing. This method is a factory method that
        initializes the chunk and its child chunks. It ensures that the chunk is a singleton and that it is not
        directly instantiated. The method also handles the initialization of child chunks and sets their state.

        :return: Weak reference to the singleton instance of the chunk.
        :rtype: weakref.ReferenceType[MainChunkType]
        """

        if cls._instance is None:
            cls._init_lock = False
            cls._instance = typing.cast(MainChunkType, cls(None))
            cls._init_lock = True

        assert cls._instance
        return weakref.ref(cls._instance)

    def __init__(self, main: None | MainChunk[MainChunkType, ContextType]):
        cls = type(self)

        _dbg(f"Initializing {cls.__qualname__} chunk ...")

        if __debug__:
            if cls is MainChunk:
                raise TypeError(f"{cls.__name__} should not be used directly")

            if cls._instance is not None:
                raise AssertionError(f"{cls.__name__} is a singleton class")

            if cls._init_lock:
                raise AssertionError(f"{cls.__name__} can only be created using the create method")

        self.main = typing.cast(MainChunkType, main)

        self._invoke_state = InvokeState._NOT_CALLED

        for attr, chunk_cls in self.chunks.items():
            chunk_cls._init_lock = False
            if main:
                _dbg(f"{chunk_cls.__qualname__} inited with {main}")
                chunk = chunk_cls(main)
            else:
                _dbg(f"{chunk_cls.__qualname__} inited with {self}, this is the main chunk")
                chunk = chunk_cls(self)
            chunk_cls._init_lock = True
            setattr(self, attr, chunk)

        cls._instance = typing.cast(MainChunkType, self)

        _dbg(f"{cls.__qualname__} initialized.")

    def invoke(self, context: ContextType) -> InvokeState:
        """Invokes the main chunks in order and manages their state. This method checks if the invoke method has
        already been called. If it has, it returns the current state. If not, it iterates through each chunk,
        invoking them in sequence. If any chunk fails to invoke, it cancels all previously invoked chunks and
        sets the invoke state to FAILED. If all chunks are invoked successfully, it sets the invoke state to
        :attr:`InvokeState.SUCCESSFUL`.
        This method is responsible for managing the lifecycle of the chunks and ensuring that they are
        properly initialized and invoked in the correct order.

        :param context: The context in which the invocation occurs.
        :type context: ContextType
        :return: The state after invocation, either :attr:`InvokeState.SUCCESSFUL` or :attr:`InvokeState.FAILED`.
        :rtype: InvokeState
        """

        cls = self.__class__

        _dbg(f"Invoking chunk: {cls.__name__}...")

        if not cls.chunks:
            _dbg(f"{cls.__name__} has no child chunks, successful")
            self._invoke_state = InvokeState.SUCCESSFUL
            return InvokeState.SUCCESSFUL

        if self._invoke_state != InvokeState._NOT_CALLED:
            _dbg(f"{cls.__name__} previously was called already. Status remains \'{self._invoke_state.name}\'")
            return self._invoke_state

        chunks_invocation_began = []

        for attr in self.chunks.keys():
            chunk: MainChunk = getattr(self, attr)
            chunks_invocation_began.append(chunk)

            _dbg(f"Invoking child chunk \"{attr}\" ({chunk.__class__.__name__})...")

            if chunk.invoke(context) != InvokeState.SUCCESSFUL:
                log.info(f"Failed to invoke child chunk {attr}, cancelling")
                break

            _dbg(f"Child chunk \"{attr}\" ({chunk.__class__.__name__}) invoked successfully")
        else:
            self._invoke_state = InvokeState.SUCCESSFUL
            _dbg(f"Chunk {cls.__name__} invoked successfully")
            return self._invoke_state

        if chunks_invocation_began:
            _dbg(f"Invocation of {cls.__name__} was failed, restoring {len(chunks_invocation_began)} chunks...")

            failed_to_cancel = []
            for chunk in reversed(chunks_invocation_began):
                if chunk.cancel(context) == InvokeState.FAILED:
                    failed_to_cancel.append(chunk)
                    _warn(f"Failed to cancel {chunk.__class__.__name__} invocation after failure")

            if failed_to_cancel:
                _dbg(
                    f"Unable to restore children chunks: {', '.join((_.__class__.__name__) for _ in failed_to_cancel)}")
            else:
                _dbg(f"Cancelled all children chunks which was already invoked")
        else:
            _dbg(f"None of chunks was invoked, nothing to restore.")

        self._invoke_state = InvokeState.FAILED
        return self._invoke_state

    def cancel(self, context: ContextType) -> InvokeState:
        """Cancels the execution of all chunks in reverse order. This method iterates over all chunks defined in the
        class in reverse order and attempts to cancel each one. If any chunk fails to cancel, a warning is logged and
        the method returns FAILED. If all chunks are successfully canceled, the method returns
        :attr:`InvokeState.SUCCESSFUL`. This method is responsible for managing the lifecycle of the chunks and ensuring
        that they are properly cleaned up and released.

        :param context: The context in which the cancellation is being performed.
        :type context: ContextType
        :returns: The state after cancellation, either :attr:`InvokeState.SUCCESSFUL` or :attr:`InvokeState.FAILED`.
        :rtype: InvokeState
        """

        cls = self.__class__
        _dbg(f"Cancelling chunk: {cls.__name__}...")

        cls._instance = None

        if not cls.chunks:
            _dbg(f"{cls.__name__} has no child chunks, successful")
            return InvokeState.SUCCESSFUL

        if self._invoke_state != InvokeState.SUCCESSFUL:
            return self._invoke_state

        failed_to_cancel = []

        for attr in reversed(list(cls.chunks)):
            chunk: MainChunk = getattr(self, attr)

            if chunk.cancel(context) == InvokeState.FAILED:
                failed_to_cancel.append(chunk)
                _warn(f"Failed to cancel \"{attr}\" ({chunk.__class__.__name__}) chunk")

        if failed_to_cancel:
            _dbg(f"Unable to cancel children chunks: {', '.join((_.__class__.__name__) for _ in failed_to_cancel)}")
            return InvokeState.FAILED
        else:
            _dbg(f"Cancelled all children chunks")
            return InvokeState.SUCCESSFUL
