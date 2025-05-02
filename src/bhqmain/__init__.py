# SPDX-FileCopyrightText: 2020-2025 Ivan Perevala <ivan95perevala@gmail.com>
#
# SPDX-License-Identifier: MIT

"""Initialization framework for Blender extensions."""

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
