# 705. Design HashSet (Easy) - direct-address table: a boolean array indexed by the key itself. O(1) time per operation, O(max key) space.
class MyHashSet:

    def __init__(self):
       # A boolean flag PER POSSIBLE KEY, not a hash table in the usual sense -
       # this is direct addressing. Sized to 1,000,001 to cover every key up
       # to the stated upper bound of 10^6 inclusive (indices 0..10^6).
       self.set = 1000001 * [False]

    def add(self, key: int) -> None:
        self.set[key] = True

    def remove(self, key: int) -> None:
        self.set[key] = False

    def contains(self, key: int) -> bool:
        return self.set[key]


# Your MyHashSet object will be instantiated and called as such:
# obj = MyHashSet()
# obj.add(key)
# obj.remove(key)
# param_3 = obj.contains(key)
