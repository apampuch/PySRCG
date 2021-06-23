from tkinter import IntVar
from typing import Callable


class Adjustment:
    karma_cost: int
    order: int
    type: str
    undo: Callable

    def __init__(self, karma_cost, type_, undo, debug_note=""):
        self.karma_cost = karma_cost
        self.order = None
        self.type = type_
        self.undo = undo
        self.debug_note = debug_note


class AdjustmentsContainer(IntVar):
    def __init__(self):
        super().__init__()
        self.container = []

    def add(self, adj):
        filtered = filter(lambda x: x.type == adj.type, self.container)
        sorted_filtered = sorted(filtered, key=lambda x: x.order, reverse=True)

        # if we have nothing of that type, set order to 0
        if len(list(sorted_filtered)) == 0:
            adj.order = 0
        # if we have one of that type, set its order to the highest of that order plus 1
        else:
            adj.order = sorted_filtered[0].order + 1

        self.container.append(adj)
        self.set(self.total)  # callback

    # returns true if the container has an adjustment with the given type
    def __contains__(self, type_):
        return type_ in (adj.type for adj in self.container)

    def make_and_add(self, karma_cost, type_, undo):
        """Add and auto-increment order"""
        adj = Adjustment(karma_cost, type_, undo)
        self.add(adj)

    def reset(self):
        """Call undo for everything and clear the container"""
        sorted_container = sorted(self.container, key=lambda x: x.order, reverse=True)
        for adj in sorted_container:
            adj.undo()

        self.container.clear()
        self.set(self.total)  # callback

    def undo_latest(self, type_):
        """Find the latest of the chosen type, then call undo for it."""
        filtered = filter(lambda x: x.type == type_, self.container)
        sorted_filtered = sorted(filtered, key=lambda x: x.order, reverse=True)

        if len(list(sorted_filtered)) == 0:
            print("Nothing with type " + type_ + "!")
            return
        # debug stuff
        # else:
        #     print(sorted_filtered[0].order)

        sorted_filtered[0].undo()
        self.container.remove(sorted_filtered[0])
        self.set(self.total)  # callback

    # override get because we're not a REAL IntVar
    def get(self):
        return self.total

    @property
    def total(self):
        total = 0
        for adj in self.container:
            total += adj.karma_cost

        return total
