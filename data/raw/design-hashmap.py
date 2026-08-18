class MyHashMap:

    def __init__(self):
        self.buckets = [[] for _ in range(1000)]

    def put(self, key: int, value: int) -> None:
        bucket = self.buckets[key % 1000]

        for pair in bucket:
            if pair[0] == key:
                pair[1] = value
                return
        bucket.append([key, value])

    def get(self, key: int) -> int:
        bucket = self.buckets[key % 1000]

        for pair in bucket:
            if pair[0] == key:
                return pair[1]
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
