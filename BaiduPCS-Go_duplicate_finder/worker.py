#!/usr/bin/env python3

import platform
import re

GROUPING = 10  # Change this value to group files for "delete.sh"

if "windows" in platform.platform():
    platform_encoding = "gbk"
    deleter_name = "delete.bat"
else:
    platform_encoding = "utf-8"
    deleter_name = "delete.sh"

pattern_s = r'BaiduPCS-Go rapidupload -length=(\d+) -md5=([0-9a-f]+) "(.*)"'
pattern = re.compile(pattern_s)

seen = {}
with open("export.txt", "r", encoding="utf-8") as f:
    for line in f:
        match = pattern.match(line.strip())
        if match is None:
            continue

        key = int(match.group(1)), match.group(2)
        if key not in seen:
            seen[key] = [match.group(3)]
        else:
            seen[key].append(match.group(3))

seen = {k: seen[k] for k in seen if len(seen[k]) >= 2}

print("Total duplicated items: {}".format(len(seen)))
print("Total duplicates: {}".format(sum(len(seen[k]) for k in seen)))
print("Inflated size: {}".format(sum(k[0] * (len(seen[k]) - 1) for k in seen)))
for key in seen:
    print("Duplicate: " + "\n           ".join(seen[key]))

deleting = sum(seen[key][1:] for key in seen)
with open(deleter_name, "w", encoding=platform_encoding) as f:
    for i in range(deleting // GROUPING):
        part = deleting[i * GROUPING: (i + 1) * GROUPING]
        print('BaiduPCS-Go rm ' + ' '.join('"{}"'.format(item) for item in part), file=f)
