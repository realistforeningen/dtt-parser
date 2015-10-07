from parser import readlatestfile

ts = None
for order in readlatestfile('sources'):
    ts = order.timestamp

print "Latest registered transaction:"
print ts

