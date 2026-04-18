from loguru import logger

from plyze.jpg.interfaces import JPGraph, JPNode, JPNodeData
import math


def is_even(k: int):  # TODO: put in utilsl4plans
    if k % 2 == 0:
        return True
    return False


def determine_node_pairs(k: int):
    n = k
    curr_level = 1

    node_nums = []
    levels = []

    while n >= 1:
        node_nums.append(n)
        levels.append(curr_level)
        logger.debug(f"num_nodes: {n}, levels: {curr_level}")

        # n = math.ceil(n / 2 ** (curr_level))
        n = math.ceil(n / 2)  # half on iteration
        curr_level += 1

        if n > 1:
            continue

        elif n == 1:
            node_nums.append(n)
            levels.append(curr_level)
            break

        if n < 1:
            break

    return node_nums, levels


def determine_mapping(node_nums: list[int], levels: list[int]):
    top_half = {}
    bottom_half = {}
    max_level = max(levels)
    for level, node_num in zip(reversed(levels), node_nums):
        bottom_half[level] = node_num

    count = 1
    for node_num in node_nums[1:]:
        top_half[max_level + count] = node_num
        count += 1

    return top_half, bottom_half


def realize_graph(mapping: dict[int, int]):
    def make_jpnode(name: str, level: int):
        return JPNode(name=name, data=JPNodeData(is_carrier=False, level=level))

    nodes = []

    for level, node_num in mapping.items():
        for node in range(node_num):
            name = f"{level}_{node}"
            nodes.append(make_jpnode(name, level))

    graph = JPGraph.create("", nodes, [])
    return graph


def make_diamond_graph(k: int, debug: bool = False):
    """Creates a scalable justified plan graph with shape of diamond. See Hillier and Hanson 1984, chapter 3, section 2.04. Note that these scalable graphs do not have a "carrier node" and thus have no "level 0". Using floored division to handle non-even values..

    Args:
        k (int): Number of spaces at the mean depth level
    Returns:
        graph (JPGraph)
    Raises:
        NotImplementedError: If k is not even.
    """

    node_nums, levels = determine_node_pairs(k)
    top_half, bottom_half = determine_mapping(node_nums, levels)
    graph = realize_graph(bottom_half | top_half)

    if debug:
        logger.debug(graph.show())

    return graph
