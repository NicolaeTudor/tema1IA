from __future__ import annotations

import copy
import hashlib
from dataclasses import dataclass, field
from functools import cached_property
from typing import List, Callable, Optional

import color
from container import Container
import graph


@dataclass
class Node:
    graph: graph.Graph = field(repr=False)
    parent: Optional[Node]
    container_from_idx: int
    container_to_idx: int
    # h: Callable[[], int]
    # state: List[Container] = field(init=False)
    # state_hash: HASH = field(init=False)
    cost_from_root: int = field(init=False)
    # estimated_cost: int = field(init=False)

    def __post_init__(self):
        if self.parent is None:
            self.cost_from_root = 0
        else:
            self.cost_from_root = self.parent.cost_from_root + 1

    @cached_property
    def state(self) -> List[Container]:
        state_copy = copy.deepcopy(self.parent.state)
        container_from = state_copy[self.container_from_idx]
        container_to = state_copy[self.container_to_idx]

        fill_to_capacity = container_to.max_cap - container_to.occupied
        capacity_to_transfer = min(fill_to_capacity, container_from.occupied)
        container_from.occupied -= capacity_to_transfer
        container_to.occupied += capacity_to_transfer
        container_to.color = color.ColorSrv().get_combination_result(container_from.color, container_to.color)
        if container_from.occupied == 0:
            container_from.color = 0

        return state_copy

    @cached_property
    def state_hash(self) -> bytes:
        s_hash = hashlib.sha256()
        for index, container in enumerate(self.state):
            s_hash.update(bytes(str(index), encoding='utf-8'))
            s_hash.update(b'_')
            s_hash.update(bytes(str(container.occupied), encoding='utf-8'))
            s_hash.update(b'_')
            s_hash.update(bytes(str(container.color), encoding='utf-8'))
            s_hash.update(b'_')
        return s_hash.digest()

    @cached_property
    def estimated_cost(self) -> int:
        return self.cost_from_root + self.graph.heuristic(self)

    def get_road(self) -> str:
        ret_val = ''
        if self.parent is not None:
            ret_val += self.parent.get_road()

            ret_val += f'Step {self.cost_from_root}: ' \
                       f'Transferred from container {self.container_from_idx} ' \
                       f'to container {self.container_to_idx}. ' \
                       f'Got color `{color.ColorSrv().get_color(self.state[self.container_to_idx].color)}` ' \
                       f'with quantity {self.state[self.container_to_idx].occupied}.\n\n'

        for i, cont in enumerate(self.state):
            ret_val += f'{i}: Capacity: {cont.max_cap}, Qty: {cont.occupied}, Color: {color.ColorSrv().get_color(cont.color)}\n'

        ret_val += '\n'
        return ret_val

    def cycles_back(self) -> bool:
        ancestor = self.parent
        while ancestor is not None:
            if self.state_hash == ancestor.state_hash:
                if self.state == ancestor.state:
                    return True
            ancestor = ancestor.parent
        return False

    @cached_property
    def usable_qty(self) -> int:
        usable_qty = 0
        for cont in self.state:
            if cont.color != -1:
                usable_qty += cont.occupied

        return usable_qty
