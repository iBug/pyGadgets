#!/usr/bin/python3

import math
import sys

if len(sys.argv) not in [2, 3]:
    sys.exit("Requires 1 or 2 arguments")

num = int(sys.argv[1])
if num < 10000:
    keys = num
else:
    full_score = num
    keys = 100 + (full_score - 37260) // 600

full_score = (keys - 100) * 600 + 37260

def score_thresh(thresh: float) -> int:
    return math.ceil(full_score * thresh)

print(f"Keys:       {keys}")
print(f"Full score: {full_score}")
print(f"99.8%:      {score_thresh(0.998)}")
print(f"SSS score:  {score_thresh(0.995)}")
print(f"SS score:   {score_thresh(0.975)}")
print(f"S score:    {score_thresh(0.95)}")
print(f"A score:    {score_thresh(0.9)}")
print(f"B score:    {score_thresh(0.8)}")
print(f"C score:    {score_thresh(0.6)}")

if len(sys.argv) == 3:
    score = int(sys.argv[2])
    print(f"Score {score} = {score / full_score:.2%}")
