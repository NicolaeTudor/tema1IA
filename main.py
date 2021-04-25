# documentatie: https://docs.google.com/document/d/1cK6_WphKj1ZMaHIuswtB2_ANYM1SmVfv-Z74e_s8pQ0/edit?usp=sharing

import os
import sys
from math import ceil
from typing import Tuple

from container import Container
from argparse import ArgumentParser
from time import time

import custom_heap
import node
import color
from graph import Graph

INIT_STATE_LINE_SEPARATOR = "stare_initiala"
FINAL_STATE_LINE_SEPARATOR = "stare_finala"

parser = ArgumentParser(usage=__file__ + ' '
                                         '-i/--input '
                                         '-o/--output'
                                         '-n/--nsol'
                                         '-t/--timeout',
                        description='Solution generator for the water containers problem')

parser.add_argument('-i', '--input',
                    dest='input',
                    default='./input',
                    help='Input folder')

parser.add_argument('-o', '--output',
                    dest='output',
                    default='./output',
                    help='Output folder')

parser.add_argument('-n', '--nsol',
                    dest='nsol',
                    default=1,
                    type=int,
                    help='Number of generated solutions')

parser.add_argument('-t', '--timeout',
                    dest='timeout',
                    default=10,
                    type=int,
                    help='Number of seconds till timeout')

# Parse arguments
args = vars(parser.parse_args())

def print_solution(output_f, max_in_mem, nr_sol, nr_successors, selected_node, sol_cnt, start_time):
    sol_cnt += 1
    output_f.write(f"Solution {sol_cnt}\n"
          f"-found in {ceil(time() - start_time)} seconds.\n"
          f"-generated {nr_successors} nodes, "
          f"with a maximum of {max_in_mem} nodes in memory.\n\n"
          f"Steps:\n")
    output_f.write(selected_node.get_road())
    nr_sol -= 1
    return nr_sol, sol_cnt


def ucs(output_f, gr: Graph, nr_sol: int = 1, timeout: int = 0):
    output_f.write("\n\n############################################################################\n\n")
    output_f.write("Started algorithm UCS\n")

    start_time, nr_successors, max_in_mem, sol_cnt = time(), 0, 1, 0
    expanded_nodes = custom_heap.CustomHeap([gr.root], key=lambda x: x.cost_from_root)
    flag = False if timeout == 0 else True

    while len(expanded_nodes.data) > 0:
        selected_node = expanded_nodes.pop()

        if flag:
            if round(time() - start_time) >= timeout:
                output_f.write("Solution stopped due to timeout\n")
                break

        if gr.test_final(selected_node):
            nr_sol, sol_cnt = print_solution(output_f, max_in_mem, nr_sol, nr_successors, selected_node, sol_cnt, start_time)
            if nr_sol == 0 or selected_node == gr.root:
                break

        successors = gr.generate_successors(selected_node)
        nr_successors += len(successors)
        for s in successors:
            expanded_nodes.push(s)
        max_in_mem = max(max_in_mem, len(expanded_nodes.data) + len(successors))

    if nr_sol != 0:
        output_f.write("All paths exhausted! No solution left.\n")
    output_f.write(f"Finished in {ceil(time() - start_time)} seconds.")
    output_f.write("\n\n###############################################\n\n")


def a_star(output_f, gr: Graph, nr_sol: int = 1, timeout=0):
    output_f.write("\n\n############################################################################\n\n")
    output_f.write("Started algorithm A*\n")

    start_time, nr_successors, max_in_mem, sol_cnt = time(), 0, 1, 0
    expanded_nodes = custom_heap.CustomHeap([gr.root], key=lambda x: x.estimated_cost)
    flag = False if timeout == 0 else True

    while len(expanded_nodes.data) > 0:
        selected_node = expanded_nodes.pop()

        if flag:
            if round(time() - start_time) >= timeout:
                output_f.write("Solution stopped due to timeout\n")
                break

        if gr.test_final(selected_node):
            nr_sol, sol_cnt = print_solution(output_f, max_in_mem, nr_sol, nr_successors, selected_node, sol_cnt, start_time)
            if nr_sol == 0 or selected_node == gr.root:
                break

        successors = gr.generate_successors(selected_node)
        nr_successors += len(successors)
        for s in successors:
            expanded_nodes.push(s)
        max_in_mem = max(max_in_mem, len(expanded_nodes.data) + len(successors))

    if nr_sol != 0:
        output_f.write("All paths exhausted! No solution left.\n")
    output_f.write(f"Finished in {ceil(time() - start_time)} seconds.")
    output_f.write("\n\n###############################################\n\n")


def a_star_opt(output_f, gr: Graph, nr_sol: int = 1, timeout=0):
    output_f.write("\n\n############################################################################\n\n")
    output_f.write("Started algorithm A* optimal\n")

    start_time, nr_successors, max_in_mem, sol_cnt = time(), 0, 1, 0
    expanded_nodes = custom_heap.CustomHeap([gr.root], key=lambda x: x.estimated_cost)
    closed_nodes = list()
    flag = False if timeout == 0 else True

    while len(expanded_nodes.data) > 0:
        selected_node = expanded_nodes.pop()

        if flag:
            if round(time() - start_time) >= timeout:
                output_f.write("Solution stopped due to timeout\n")
                break

        if gr.test_final(selected_node):
            nr_sol, sol_cnt = print_solution(output_f, max_in_mem, nr_sol, nr_successors, selected_node, sol_cnt, start_time)
            if nr_sol == 0 or selected_node == gr.root:
                break

        successors = gr.generate_successors(selected_node)
        successors_cpy = successors.copy()
        nr_successors += len(successors)
        found_in_open = True
        append_to_open = True
        for s in successors_cpy:
            for target in expanded_nodes.data:
                if s.state_hash == target[2].state_hash:
                    if s.state == target[2].state:
                        found_in_open = True
                        if s.estimated_cost < target[2].estimated_cost:
                            expanded_nodes.data.remove(target)
                            expanded_nodes.heapify()
                        else:
                            append_to_open = False
                        break

            if not found_in_open:
                for close_idx, target in enumerate(closed_nodes):
                    if s.state_hash == target.state_hash:
                        if s.state == target.state:
                            if s.estimated_cost < target.estimated_cost:
                                closed_nodes[close_idx] = closed_nodes[-1]
                                closed_nodes.pop()
                            else:
                                append_to_open = False
                            break
            if append_to_open:
                expanded_nodes.push(s)

        max_in_mem = max(max_in_mem, len(expanded_nodes.data) + len(successors) + len(closed_nodes))
        closed_nodes.append(selected_node)

    if nr_sol != 0:
        output_f.write("All paths exhausted! No solution left.\n")
    output_f.write(f"Finished in {ceil(time() - start_time)} seconds.")
    output_f.write("\n\n###############################################\n\n")


def ida_star(output_f, gr: Graph, nr_sol: int = 1, timeout=0):
    def construct_road(target_node: node.Node) -> int:
        nonlocal start_time, nr_successors, max_in_mem, sol_cnt, nr_sol, flag, limit, output_f, gr

        if flag:
            if round(time() - start_time) >= timeout:
                output_f.write("Solution stopped due to timeout\n")
                return -1

        if target_node.estimated_cost > limit:
            return target_node.estimated_cost

        if gr.test_final(target_node) and target_node.estimated_cost == limit:
            nr_sol, sol_cnt = print_solution(output_f, max_in_mem, nr_sol, nr_successors, target_node, sol_cnt, start_time)
            if nr_sol == 0 or target_node == gr.root:
                return 0

        max_in_mem += 1
        minim = -1
        successors = gr.generate_successors(target_node)
        nr_successors += len(successors)
        for s in successors:
            s_rez = construct_road(s)
            if s_rez == 0:
                return 0
            if minim == -1 or s_rez < minim:
                minim = s_rez

        return minim

    output_f.write("\n\n############################################################################\n\n")
    output_f.write("Started algorithm IDA*\n")
    start_time, nr_successors, max_in_mem, sol_cnt = time(), 0, 1, 0
    flag = False if timeout == 0 else True
    limit = gr.root.estimated_cost

    while True:
        rez = construct_road(gr.root)
        if rez == 0:
            break
        if rez == -1:
            return

        limit = rez

    if nr_sol != 0:
        output_f.write("All paths exhausted! No solution left.\n")
    output_f.write(f"Finished in {ceil(time() - start_time)} seconds.")
    output_f.write("\n\n###############################################\n\n")


if __name__ == "__main__":
    n_sol = args['nsol']
    timeout_arg = args['timeout']

    colorSrv = color.ColorSrv()
    for numeFisier in os.listdir(args['input']):
        print("Input:", numeFisier)
        f_in = open(args['input'] + '/' + numeFisier)
        f_out = open(args['output'] + '/' + "output_" + numeFisier, "w")
        line = f_in.readline()
        while line.strip() != INIT_STATE_LINE_SEPARATOR:
            color_l, color_r, color_f = line.split()
            code_l = colorSrv.add_color(color_l)
            code_r = colorSrv.add_color(color_r)
            code_f = colorSrv.add_color(color_f)
            colorSrv.add_combination(code_l, code_r, code_f)
            line = f_in.readline()

        init_state = []
        line = f_in.readline()
        while line.strip() != FINAL_STATE_LINE_SEPARATOR:
            container_values = line.split()
            max_cap = int(container_values[0])
            occupied = int(container_values[1])
            code = 0
            if occupied != 0:
                color = container_values[2]
                code = colorSrv.add_color(color)
            init_state.append(Container(max_cap, occupied, code))
            line = f_in.readline()

        final_state = []
        line = f_in.readline()
        while line:
            container_values = line.split()
            cap = int(container_values[0])
            color = container_values[1]
            code = colorSrv.get_code(color)
            final_state.append(Container(0, cap, code))
            line = f_in.readline()

        graph = Graph(final_state, init_state, n_sol)

        ucs(f_out, graph, n_sol, timeout_arg)

        for h_code in range(4):
            output = graph.set_heuristic(h_code)
            f_out.write(output)
            a_star(f_out, graph, n_sol, timeout_arg)
            a_star_opt(f_out, graph, n_sol, timeout_arg)
            ida_star(f_out, graph, n_sol, timeout_arg)
            f_out.write("\n\n#####################################################################################\n\n")

        colorSrv.reset()
        f_in.close()
        f_out.close()
