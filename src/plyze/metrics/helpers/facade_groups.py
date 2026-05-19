from collections import UserDict


class WindowGroupsDict(UserDict):
    # Example method 1: Get all keys with values above a threshold
    def keys_with_north(self):
        return [v for k, v in self.data.items() if "N" in k]


FACADE_GROUPS = {
    frozenset({"N", "E", "S", "W"}): 0,
    frozenset({"N", "E", "S"}): 1,
    frozenset({"N", "E", "W"}): 2,
    frozenset({"N", "S", "W"}): 3,
    frozenset({"E", "S", "W"}): 4,
    frozenset({"N", "E"}): 5,
    frozenset({"N", "S"}): 6,
    frozenset({"N", "W"}): 7,
    frozenset({"E", "S"}): 8,
    frozenset({"E", "W"}): 9,
    frozenset({"S", "W"}): 10,
    frozenset({"N"}): 11,
    frozenset({"E"}): 12,
    frozenset({"S"}): 13,
    frozenset({"W"}): 14,
}
