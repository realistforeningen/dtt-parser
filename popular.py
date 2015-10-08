from collections import defaultdict
from parser import readdir
from datetime import datetime
import sys

if len(sys.argv) != 2:
    print "usage: python popular.py YEAR-MONTH-DAY"
    print
    print "Reports the number of sold units for each product since the given date."
    sys.exit(1)

min_date = datetime.strptime(sys.argv[1], '%Y-%m-%d')

names = {}
counts = defaultdict(lambda:0)

print "Reading files..."

for order in readdir('sources'):
    if order.timestamp > min_date:
        for entry in order.entries:
            counts[entry.product_id] += entry.count
            names[entry.product_id] = entry.name

print "Result: Most sold products since %s" % min_date

keys = sorted(counts.keys(), key=lambda key: -counts[key])
for key in keys:
    print "%s: %s (%d sold units)" % (key, names[key], counts[key])

