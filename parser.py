import os
from datetime import datetime, date
from collections import defaultdict

class Entry:
    pass

class Order:
    pass

def readfiles(files):
    last_ts = datetime.min

    for fname in files:
        parser = DTT(open(fname))

        for order in parser:
            if order.timestamp < last_ts:
                continue
            yield order
            last_ts = order.timestamp

def expanddir(directory):
    files = os.listdir(directory)
    files.sort()
    return [os.path.join(directory, fname) for fname in files]

def readdir(directory):
    files = expanddir(directory)

    for order in readfiles(files):
        yield order

def readlatestfile(directory):
    fname = expanddir(directory)[-1]
    for order in readfiles([fname]):
        yield order

class DTT:
    def __init__(self, stream):
        self.stream = stream

    def __iter__(self):
        entries = []

        for line in self.stream:
            if line[:2] in ('A ', 'J ', 'K'):
                entry = Entry()

                entry.product_id = int(line[3:6])
                entry.name = line[7:27].decode('latin-1').strip()
                entry.count = int(line[28:32])
                entry.total_price = int(line[35:40])*100 + int(line[41:43])
                entries.append(entry)

            if line.startswith(' <'):
                if len(entries) == 0:
                    # No entries. Nevermind.
                    continue

                ts = datetime.strptime(line[2:16], '%d-%m-%y %H:%M')
                order = Order()
                order.timestamp = ts
                order.entries = entries
                yield order

                entries = []

if __name__ == '__main__':
    import sys

    global report_counter
    report_counter = 1

    report_lines = open('reports.txt').readlines()
    report_dates = [datetime.strptime(x.strip(), '%Y-%m-%d %H:%M') for x in report_lines]

    def reset_counts():
        global counts
        counts = defaultdict(lambda: {"count":0})

    def dump_counts():
        global report_counter
        with open('reports/%03d.txt' % report_counter, 'w') as f:
            for key in counts:
                data = counts[key]
                f.write("%s\t%s: %s\t%s\tKassasalg\n" % (data["timestamp"], key, data["name"].encode('utf-8'), -data["count"]))

        report_counter += 1

    reset_counts()

    for order in readdir('sources'):
        if order.timestamp < report_dates[0]:
            # We've not yet reached our destination
            continue

        while len(report_dates) > 1 and order.timestamp > report_dates[1]:
            # Oh uh. We've way beyond our range. Jump to the next date!
            report_dates.pop(0)
            dump_counts()
            reset_counts()

        if len(report_dates) == 1:
            break

        for entry in order.entries:
            data = counts[entry.product_id]
            data["count"] += entry.count
            data["name"] = entry.name
            if "timestamp" not in data:
                data["timestamp"] = order.timestamp

    while len(report_dates) > 1:
        report_dates.pop(0)
        dump_counts()
        reset_counts()

