class Solution:
    def dailyTemperatures(self, temperatures: list[int]) -> list[int]:
        

        answer = [0] *len(temperatures)

        waiting = []

        for index, value in enumerate(temperatures):

            while waiting and temperatures[waiting[-1]] < value:

                settled = waiting.pop()

                answer[settled] = index - settled
            
            waiting.append(index)
        
        return answer
