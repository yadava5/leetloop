# 706. Design HashMap (Easy) - chaining hash table: 1000 buckets, each a list of [key, value] pairs, linear scan within a bucket. O(1) expected per operation, O(n) worst case if many keys collide.
class MyHashMap:

    def __init__(self):
        # 1000 buckets. Each key lands in bucket key % 1000, and collisions
        # within a bucket are resolved by chaining - a plain list of pairs.
        self.buckets = [[] for _ in range(1000)]

    def put(self, key: int, value: int) -> None:
        bucket = self.buckets[key % 1000]

        # Scan the bucket for an existing entry with this key so put() can
        # UPDATE in place rather than append a duplicate. Mutating pair[1]
        # directly (rather than rebuilding the pair) keeps this an O(1)
        # in-place update once the matching entry is found.
        for pair in bucket:
            if pair[0] == key:
                pair[1] = value
                return
        # No existing entry for this key: append a new [key, value] pair.
        bucket.append([key, value])

    def get(self, key: int) -> int:
        bucket = self.buckets[key % 1000]

        for pair in bucket:
            if pair[0] == key:
                return pair[1]
        # Key was never put(), or was removed: the problem defines this as -1.
        return -1

    def remove(self, key: int) -> None:
        bucket = self.buckets[key % 1000]

        for pair in bucket:
            if pair[0] == key:
                bucket.remove(pair)
                return


# Your MyHashMap object will be instantiated and called as such:
# obj = MyHashMap()
# obj.put(key,value)
# param_2 = obj.get(key)
# obj.remove(key)
