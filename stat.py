# Some statistics functions

from math import sqrt

def avg(l):
    try:
        return sum(l) / len(l)
    except ZeroDivisionError:
        raise ValueError("The list cannot be empty")

def stddev(l, a=None, unbiased=0):
    if a is None:
        a = avg(l)
    return sqrt(sum([(i-a)**2 for i in l]) / (len(l) - unbiased))

def ubstddev(l, a=None):
    return stddev(l, a=a, unbiased=1)

def bstddev(l, a=None):
    return stddev(l, a=a, unbiased=0)
