# SPDX-FileCopyrightText: 2020-2025 Ivan Perevala <ivan95perevala@gmail.com>
#
# SPDX-License-Identifier: MIT

"""
Lightweight library that helps structure code into chunks. The idea is simple: there is a main chunk and derived chunks.
When the `invoke` method of the main chunk is called, it invokes all derived chunks, and the same applies to the
`cancel` method. The actual implementation handles situations where one of the chunks is unable to invoke or
cancel - in this case, all previously invoked chunks will be cancelled, and information about what happened will
be logged.
"""

from __future__ import annotations

if __debug__:
    def __reload_submodules(lc):
        import importlib

        if "_main" in lc:
            importlib.reload(_main)

    __reload_submodules(locals())
    del __reload_submodules

from . import _main

from . _main import MainChunk, MainChunkType, InvokeState

__all__ = (
    # file://./_main.py
    "MainChunk",
    "MainChunkType",
    "InvokeState",
)
