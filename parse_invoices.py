#!/usr/bin/env python3

import re
import sys
import glob
import subprocess as sp
import pprint
import functools

def no_float(x):
    if x == ',':
        return 0
    return float(x.replace('.', '').replace(' ', '').replace(',', '.'))

s = {}

for fname in glob.glob(sys.argv[1] + 'vectura*.pdf'):
    print(fname)
    f = str(sp.check_output(['pdftotext', '-fixed', '4', fname, '-']), 'utf-8')
    for line in f.split('\n'):
        if line.startswith(' '*9) and not line.startswith(' '*10):
            number = int(line[9:15])
            name = line[18:43].strip()
            count = int(line[69:75])
            pack = line[76:79].strip()
            unit_price = no_float(line[80:91].strip(' 0'))
            total = no_float(line[117:127].strip())
            net_price = no_float(line[132:142].strip())
            k = (number, name, pack, unit_price)
            s[k] = s[k] + count if k in s else count

vinhuset = {}

for fname in glob.glob(sys.argv[1] + 'vinhuset*.pdf'):
    print(fname)
    f = str(sp.check_output(['pdftotext', '-fixed', '4', fname, '-']), 'utf-8').split('\n')
    f = iter(f)
    for line in f:
        if line.startswith(' '*8) and line[8].isdigit():
            number = int(line[8:15])
            name = line[20:55].strip()
            try: # Just give me the rest of the line!
                count = int(line[114:120])
            except ValueError as e:
                line = next(f)
            pack = line[88:94].strip()
            if ' ' in pack: # Remove any part of previous column
                pack = pack.split()[-1]
            unit_price = no_float(line[103:111].strip())
            total = no_float(line[131:141].strip())
            k = (number, name, pack, unit_price)
            if count > 0:
                if k in vinhuset:
                    vinhuset[k] += count
                else:
                    vinhuset[k] = count

ringnes = {}
ringnes_pant = {}

for fname in glob.glob(sys.argv[1] + 'ringnes*.pdf'):
    print(fname)
    f = str(sp.check_output(['pdftotext', '-layout', fname, '-']), 'utf-8').split('\n')
    f = iter(f)
    for line in f:
        if len(line) > 9 and line[0].isspace() and line[6].isspace() and line[1].isdigit():
            number = int(line[1:6])
            name = line[8:47].strip().replace(' ', ' ')
            count = int(line[48:54].strip('  '))
            k = (number, name)
            if count > 0:
                if k in ringnes:
                    ringnes[k] += count
                else:
                    ringnes[k] = count
        if len(line) > 9 and line[0].isspace() and line[6].isdigit() and line[1].isdigit():
            number = int(line[1:7])
            name = line[8:47].strip().replace(' ', ' ')
            count = int(line[71:78].strip('  '))
            k = (number, name)
            if k in ringnes_pant:
                ringnes_pant[k] += count
            else:
                ringnes_pant[k] = count
        

                    
pprint.pprint(s)
pprint.pprint(vinhuset)
pprint.pprint(ringnes)
pprint.pprint(ringnes_pant)

