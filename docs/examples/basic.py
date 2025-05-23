# This example demonstrates how to use `bhqmain` library.

from __future__ import annotations

import bhqmain4 as bhqmain


class Context:
    ...
    # This class is used to store some context.


class Derived(bhqmain.MainChunk['Main', 'Context']):
    bar: bool

    def __init__(self, main):
        super().__init__(main)

        self.bar = False

    def invoke(self, context):
        self.bar = True
        return super().invoke(context)

    def cancel(self, context):
        self.bar = False
        return super().cancel(context)

    def some_method(self):
        if self.main.foo:
            self.bar = False


class Main(bhqmain.MainChunk['Main', 'Context']):
    derived: Derived

    chunks = {
        "derived": Derived,
    }

    foo: bool

    def __init__(self, main):
        super().__init__(main)

        self.foo = False

    def invoke(self, context):
        self.foo = True
        return super().invoke(context)

    def cancel(self, context):
        self.foo = False
        return super().cancel(context)

    def another_method(self):
        if self.derived.bar:
            self.foo = False


if __name__ == '__main__':
    context = Context()

    main_ref = Main.create()
    if main_ref:
        if main_ref().invoke(context) == bhqmain.InvokeState.SUCCESSFUL:
            pass

        if main_ref().cancel(context) == bhqmain.InvokeState.SUCCESSFUL:
            pass
