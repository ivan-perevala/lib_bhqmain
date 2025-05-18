# SPDX-FileCopyrightText: 2020-2024 Ivan Perevala <ivan95perevala@gmail.com>
#
# SPDX-License-Identifier: MIT

from __future__ import annotations

import pytest

import bhqmain4 as bhqmain


def test_main_direct_use_raises():
    # Test that the MainChunk class cannot be instantiated directly.
    with pytest.raises(TypeError):
        bhqmain.MainChunk.create()
