from loguru import logger

from plyze.jpg.interfaces import JPNode, JPNodeData


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

        n = n // 2**1
        curr_level += 1

        if n >= 1:
            continue

        if n < 1:
            break

    logger.debug(node_nums)
    logger.debug(levels)
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

    logger.debug(top_half)
    logger.debug(bottom_half)
    return top_half, bottom_half


def realize_graph(mapping: dict[int, int]):
    def make_jpnode(name: str, level: int):
        return JPNode(name=name, data=JPNodeData(is_carrier=False, level=level))

    for level, node_num in mapping.items():
        for node in range(node_num):
            make_jpnode()
    pass


def diamond_graph(k: int):
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

    # if not is_even(k):
    #     raise NotImplementedError(f"k={k} is not even!")
