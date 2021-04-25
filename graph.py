from __future__ import annotations

from dataclasses import dataclass, InitVar, field
from functools import cached_property
from itertools import combinations
from queue import Queue
from typing import List, Callable
from collections import Counter

import color
from container import Container
import node

INFINITY = 0x40000


@dataclass
class Graph:
    final_state: List[Container]
    init_state: InitVar[List[Container]]
    nr_sol: int
    root: node.Node = field(init=False)
    heuristic: Callable[[node.Node], int] = field(init=False, default=None)

    def __post_init__(self, init_state):
        self.root = node.Node(self, None, 0, 0)
        self.root.state = init_state

    def set_heuristic(self, heuristic_code):
        if heuristic_code == 0:
            self.heuristic = self.trivial_heuristic
            return "Using trivial heuristic\n\n"
        elif heuristic_code == 1:
            self.heuristic = self.inadmissible_heuristic
            return "Using inadmissible heuristic\n\n"
        elif heuristic_code == 2:
            self.heuristic = self.admissible_heuristic_1
            return "Using admissible heuristic no. 1\n\n"
        elif heuristic_code == 3:
            self.heuristic = self.admissible_heuristic_2
            return "Using admissible heuristic no. 2\n\n"

    def generate_successors(self, target_node: node.Node) -> List[node.Node]:
        successors = []
        for i, container_i in enumerate(target_node.state):
            for j, container_j in enumerate(target_node.state):
                if i == j:
                    continue

                if container_i.occupied == 0 or container_j.max_cap == container_j.occupied:
                    continue

                gen_node = node.Node(self, target_node, i, j)
                if not self.is_part_of_solution(gen_node):
                    continue

                successors.append(gen_node)

        return successors

    def match_final(self, target_node: node.Node) -> Counter[Container]:
        counter_target, counter_final = Counter(target_node.state), Counter(self.final_state)
        match = (counter_target & counter_final)
        return match

    def test_final(self, target_node: node.Node) -> bool:
        counter_final = Counter(self.final_state)
        match = self.match_final(target_node)
        return match == counter_final

    @cached_property
    def final_state_total_qty(self) -> int:
        total_qty = 0
        for cont in self.final_state:
            total_qty += cont.occupied

        return total_qty

    def is_part_of_solution(self, target_node: node.Node) -> bool:
        """

        Returns
        -------
            True if we can (theoretically) reach solution from given state
        """

        if target_node.cycles_back() or target_node.usable_qty < self.final_state_total_qty:
            return False

        final_state_colors = set()
        target_state_colors = set()
        missing_colors_queue = Queue()
        for cont in self.final_state:
            final_state_colors.add(cont.color)

        for cont in target_node.state:
            target_state_colors.add(cont.color)

        for final_color in final_state_colors:
            if final_color not in target_state_colors:
                missing_colors_queue.put(final_color)

        while not missing_colors_queue.empty():
            ms_color = missing_colors_queue.get()
            resulted_colors = color.ColorSrv().deconstruct_color(ms_color)
            if resulted_colors == -1:
                return False
            for new_color in resulted_colors:
                if new_color not in target_state_colors:
                    missing_colors_queue.put(new_color)

        return True

    def trivial_heuristic(self, target_node: node.Node) -> int:
        """
        Returns
        -------
            0 if final state, else 1
        """
        return 0 if self.test_final(target_node) else 1

    def inadmissible_heuristic(self, target_node: node.Node) -> int:
        """
        Estimated cost is the sum of containers matching final_state

        Returns
        -------
            estimated cost to final state
        """
        match = self.match_final(target_node)

        return len(self.final_state) - sum(match.values())

    def admissible_heuristic_1(self, target_node: node.Node) -> int:
        """
        Estimated cost is the number of missing colors from final_state

        Returns
        -------
            estimated cost to final state
        """
        final_state_colors = set()
        target_state_colors = set()
        for cont in self.final_state:
            final_state_colors.add(cont.color)

        for cont in target_node.state:
            target_state_colors.add(cont.color)

        return len(final_state_colors) - len(final_state_colors.intersection(target_state_colors))

    def admissible_heuristic_2(self, target_node: node.Node) -> int:
        """
        Estimated cost is the min number of steps to get all colors from final_state.
        If we can't reach a color from final_state we return INFINITY so we won't use it again

        Returns
        -------
            estimated cost to final state
        """
        final_state_colors = set()
        target_state_colors = set()
        missing_colors_queue = Queue()
        estimation = 0
        for cont in self.final_state:
            final_state_colors.add(cont.color)

        for cont in target_node.state:
            target_state_colors.add(cont.color)

        for final_color in final_state_colors:
            if final_color not in target_state_colors:
                missing_colors_queue.put(final_color)

        while not missing_colors_queue.empty():
            ms_color = missing_colors_queue.get()
            resulted_colors = color.ColorSrv().deconstruct_color(ms_color)
            if resulted_colors == -1:
                return INFINITY
            estimation += 1
            for new_color in resulted_colors:
                if new_color not in target_state_colors:
                    missing_colors_queue.put(new_color)

        return estimation
