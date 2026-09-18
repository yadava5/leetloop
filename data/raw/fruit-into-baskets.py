class Solution:
    def totalFruit(self, fruits: list[int]) -> int:
        
        k = 2

        if k == 0 or not fruits:
            return 0

        basket = {}

        best_total = 0
        left = 0

        for right, fruit in enumerate(fruits):

            if fruit not in basket:
                basket[fruit] = 0
            basket[fruit] += 1

            while len(basket) > k:
                basket[fruits[left]] -= 1
            
                if basket[fruits[left]] == 0:
                    del basket[fruits[left]]
                left += 1

            current_length = right - left + 1

            if best_total < current_length:
                best_total = max(best_total, current_length)
        
        return best_total
                


