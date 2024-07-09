#!/usr/bin/env python

# Find the raw bitstring from a captured Flipper RAW .sub file.
# Must provide the bitlength in ms, and the allowable error which can be tolerated.

import re
import sys
import math

filename = sys.argv[1]

bitlen = 400
allowable_error = 60
minseg = bitlen - allowable_error

def normalize(seg):
    aseg = abs(seg)
    if aseg < minseg:
        return 'x'
    n = aseg // bitlen * bitlen
    if abs(aseg - n) <= allowable_error:
        return int(math.copysign(n, seg))
    n += bitlen
    if abs(aseg - n) <= allowable_error:
        return int(math.copysign(n, seg))
    return 'x'

segs = []
with open(filename, 'r') as f:
    for line in f:
        m = re.match(r'RAW_Data:\s*([-0-9 ]+)\s*$', line)
        if m:
            segs.extend([normalize(int(seg)) for seg in m[1].split(r' ')])

full = []
for seg in segs:
    if seg == 'x':
        full.append(seg)
    elif seg > 0:
        full.extend('1' * (seg // bitlen))
    elif seg < 0:
        full.extend('0' * (-seg // bitlen))
full = ''.join(full)

print('Full bitstring:')
print(full)

def longest_repeated_contiguous_substring(s):
    return max(re.findall(r'(.+)\1', s), key=len)

lrs = longest_repeated_contiguous_substring(full)

def shortest_repeat(s):
    while m := re.fullmatch(r'(.+)\1', s):
        s = m[1]
    return s

print('Shortest repeating contiguous substring:')
print(shortest_repeat(lrs))
