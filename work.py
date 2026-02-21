from copy import copy

def shell_sort(nums):
    steps = 12
    A = copy(nums)
    n = len(nums)
    s = [0] * steps
    k = 1
    for i in range(steps-1, -1, -1):
        s[i] = k
        k = k * 2 + 1
    for i in s:
        for j in range(i, n):
            x = A[j]
            p = j - i
            
            while p >= 0 and x < A[p]:
                A[p + i] = A[p]
                p -= i
            
            A[p + i] = x
    return A