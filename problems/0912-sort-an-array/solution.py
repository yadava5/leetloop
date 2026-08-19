# 912. Sort an Array (Medium) - classic top-down merge sort, implemented with fresh list slices at every split. O(n log n) time, O(n) space per merge level.
class Solution:
    def sortArray(self, nums: List[int]) -> List[int]:

        def mergeSort(arr):

            # Base case: 0 or 1 element is trivially sorted already, and
            # splitting further would either loop forever (empty slices
            # can't shrink) or be pointless.
            if len(arr) <= 1:
                return arr

            # Split into two halves. Slicing here copies, so `left`/`right`
            # are independent lists - arr itself is never mutated.
            mid = len(arr) // 2
            left = arr[:mid]
            right = arr[mid:]

            # Sort each half FIRST, recursively, before attempting to merge -
            # merging only produces a sorted result if its two inputs are
            # already individually sorted. This ordering (sort, then merge)
            # is the entire algorithm.
            left = mergeSort(left)
            right = mergeSort(right)

            # Merge the two now-sorted halves by repeatedly taking the
            # smaller of the two current fronts. `<` (strict) rather than
            # `<=` means on a tie the LEFT half's element is taken first -
            # this is what keeps the sort stable.
            i = 0
            j = 0
            result = []

            while i < len(left) and j < len(right):
                if left[i] < right[j]:
                    result.append(left[i])
                    i += 1
                else:
                    result.append(right[j])
                    j += 1

            # One of the two halves may still have leftover elements once the
            # other is exhausted - both loops are needed since exactly one of
            # them (never both) will actually execute any iterations.
            while i < len(left):
                result.append(left[i])
                i += 1

            while j < len(right):
                result.append(right[j])
                j += 1

            return result
        return mergeSort(nums)
