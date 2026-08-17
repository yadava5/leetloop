# 27. Remove Element (Easy) - in-place compaction with a write pointer. O(n) time, O(1) extra space.
class Solution:
    def removeElement(self, nums: List[int], val: int) -> int:

        # write carries two meanings at once, and that is the whole trick:
        #   - how many keepers have been placed so far, and
        #   - the index the NEXT keeper belongs at.
        # Because those are the same number, the counter that gets returned is
        # also the pointer that does the work. No second variable, no final
        # arithmetic to convert one into the other.
        write = 0

        # The read pointer is implicit: `num` walks the list left to right,
        # each element exactly once. write only advances on a keeper, so after
        # processing index i we have write <= i + 1, which means the slot being
        # written to has ALWAYS already been read. That is why mutating nums
        # while iterating over it is safe here even though it is normally a
        # trap - the writer can never overtake the reader.
        for num in nums:
            if num != val:
                # Copy the keeper down to the front of the array. Before the
                # first deletion write == the read index and this assigns an
                # element onto itself: wasted, never wrong. Guarding it with
                # `if write != <read index>` would need an explicit read index
                # and buys nothing.
                nums[write] = num
                # WART worth knowing: `write +=1` is missing the space before
                # the 1. Valid Python, and PEP 8 wants `write += 1`.
                write +=1
        # Everything from index write onward is stale leftovers from the
        # original array - the problem states outright that those slots are
        # ignored, so there is nothing to clear or pad. Returning write is
        # returning k, the number of surviving elements, and nums[:k] is
        # already exactly those elements in their original relative order.
        return write
