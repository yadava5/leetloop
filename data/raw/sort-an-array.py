class Solution:
    def sortArray(self, nums: List[int]) -> List[int]:
        
        def mergeSort(arr):

            if len(arr) <= 1:
                return arr
            
            mid = len(arr) // 2
            left = arr[:mid]
            right = arr[mid:]

            left = mergeSort(left)
            right = mergeSort(right)

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
            
            while i < len(left):
                result.append(left[i])
                i += 1

            while j < len(right):
                result.append(right[j])
                j += 1
            
            return result
        return mergeSort(nums)
