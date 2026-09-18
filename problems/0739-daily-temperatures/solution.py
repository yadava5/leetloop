# 739. Daily Temperatures (Medium) - monotonic stack of indices still waiting for a warmer day. O(n) time, O(n) space.
class Solution:
    def dailyTemperatures(self, temperatures: list[int]) -> list[int]:

        # Prefill with 0, which is the answer for every day that never finds a
        # warmer one. That is not a placeholder to be overwritten later - it is
        # the FINAL answer for whatever is left on the stack at the end, and it
        # is why the code needs no drain loop after the main pass.
        #
        # (Style wart, left alone: `[0] *len(...)` is missing a space after the
        # star. Harmless, and the AST gate forbids fixing it here.)
        answer = [0] *len(temperatures)

        # Indices - NOT temperatures - of days that have not yet found a warmer
        # day. Storing indices is what makes the distance subtraction possible
        # at the moment of resolution; storing values would lose the position.
        # The temperatures at these indices are non-increasing from bottom to
        # top, which is the invariant the while loop maintains.
        waiting = []

        for index, value in enumerate(temperatures):

            # Today resolves every pending day that is strictly colder. Each
            # such day's first warmer day is today, because it survived every
            # day in between - had one of those been warmer, it would have
            # popped this index then.
            #
            # STRICT `<` is load-bearing. With `<=`, an equal temperature would
            # resolve the pending day, but "warmer" means strictly greater:
            # on [70, 70, 75] day 0's answer is 2, not 1.
            while waiting and temperatures[waiting[-1]] < value:

                # Pop from the top: the most recent pending day, which is also
                # the coldest on the stack. Once popped, this index is finished
                # and can never be needed again - its answer is now known.
                settled = waiting.pop()

                # Distance in days, not a temperature and not an index. The
                # subtraction is the whole reason indices were stacked.
                answer[settled] = index - settled

            # Push AFTER the while loop, never before. Pushing first would put
            # today's index on the stack and then immediately test it against
            # itself; `value < value` is false so it would not pop, but the
            # ordering here is what keeps the stack's non-increasing property
            # true at the top of every iteration.
            waiting.append(index)

        # Anything still in `waiting` never found a warmer day and keeps its
        # prefilled 0. No cleanup pass is needed.
        return answer
