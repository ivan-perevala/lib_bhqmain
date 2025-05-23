# Initialization framework for Blender extensions

[![PyPI](https://img.shields.io/pypi/v/bhqmain.svg)](https://pypi.org/project/bhqmain/)
[![Status](https://img.shields.io/pypi/status/bhqmain.svg)](https://pypi.org/project/bhqmain/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Documentation Status](https://readthedocs.org/projects/lib-bhqmain/badge/?version=latest)](https://lib-bhqmain.readthedocs.io/latest)
![Tests](https://github.com/ivan-perevala/lib_bhqmain/actions/workflows/python-tests.yml/badge.svg)
![Spell Check](https://github.com/ivan-perevala/lib_bhqmain/actions/workflows/spellcheck.yml/badge.svg)

<p align="center">
    <img src="https://raw.githubusercontent.com/ivan-perevala/lib_bhqmain/main/.github/images/logo-dark.svg" alt="Logo" style="width:50%; height:auto;">
</p>

Lightweight library that helps structure code into chunks. The idea is simple: there is a main chunk and derived chunks. When the `invoke` method of the main chunk is called, it invokes all derived chunks, and the same applies to the `cancel` method. The actual implementation handles situations where one of the chunks is unable to invoke or cancel - in this case, all previously invoked chunks will be cancelled, and information about what happened will be logged.

Links:

* Documentation: [lib-bhqmain.readthedocs.io/latest](https://lib-bhqmain.readthedocs.io/latest/)

* Project is [available on PyPI](https://pypi.org/project/bhqmain/):

    ```powershell
    pip install bhqmain
    ```


© 2024-2025 Ivan Perevala (ivan95perevala@gmail.com)
