#!/usr/bin/env python3

"""
"A " # Noe er kjøpt
"J " # Retur
"K " # Retur
"C " # Kredit
"L " # Sletta linje (ignorer)
"R " # Sum
"x " # MVA
"c " # Clear? (Ignorer)
"h " # Skuff
"B   30" # "SIGN.ANNUL"
"B " # Skuff, etc.
"-D" # ?? (ignorer)
" <" # Tid, sum
"""

import datetime
import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
import re
import sys
from glob import glob

matplotlib.style.use('ggplot')

def _new_plot(*args, **kwargs):
    pd.tools.plotting.plot_frame(*args, **kwargs)
    plt.show()
pd.DataFrame.plot = _new_plot



exec(compile(open('inventory.dict').read(), 'inventory.dict', 'exec'))

families = ('Øl',              # 0
            'Vin',             # 1
            'Rusbrus/Cider',   # 2
            'Sprit/Brennevin', # 3
            'Mineralvann',     # 4
            'Snacks',          # 5
            'Kaffe/Te',        # 6
            'Merch',           # 7
            'Diverse',         # 8
            'Engangskrus',     # 9
            'Lettbrennevin',   # 10
            'Mat',             # 11
            )
subfamilies = ('Lager',          # 0
               'Mørk Ale',       # 1
               'Lys Ale',        # 2
               'IPA',            # 3
               'Hveteøl',        # 4
               'Frukt- og surøl',# 5
               'Belgisk stil',   # 6
               'Andre stiler',   # 7
               'Alkoholfritt')   # 8
packaging = ('Bottle',
             'Can',
             'Keg',
             'Other')

#fname = sys.argv[1]

z_report = {}
transactions = []

VAT = 1.25
SHRINKAGE = 1.11

def current_price(pt, zrepdate):
    # pt = (('date', price), ('date', price), ...)
    for d, p in pt[::-1]:
        if d < zrepdate:
            return p
    return p
def test_current_price():
    assert current_price((('0', 123),), '20150520') == 123
    assert current_price((('20140701', 123), ('20150201', 321)),
                         '20150401') == 321
    assert current_price((('20140701', 123), ('20150101', 321)),
                         '20150401') == 321
    assert current_price((('20140701', 123), ('20150101', 321)),
                         '20130901') == 123

new_inv = []
    
def register(ticket, zrepdate, weekday):
    global transactions
    new_ticket = []
    for line in ticket:
        if line[:2] in (b'A ', b'J ', b'K '):
            idx = int(line[3:6])
            if not idx in inv:
                # new_inv.append(line)
                continue
            # name = str(line[7:27], encoding='latin-1')
            count = int(line[28:32])
            price = float(line[35:43])/abs(count)
            profit = round(abs(price) - current_price(inv[idx].get('price_in',
                           (('0',abs(price)/VAT/SHRINKAGE),)), zrepdate)
                           * VAT * SHRINKAGE, 2)
            if count < 0:
                profit = -profit
            is_intern = bool(line[54] == 50)
            subfamily, pack = 'Other', 'Other'
            brewery, volume = None, 0
            family = families[inv[idx]['family']]
            if inv[idx]['family'] == 0:
                subfamily = subfamilies[inv[idx]['subfamily']]
                pack = packaging[inv[idx]['packaging']]
                brewery = inv[idx]['brewery']
            abv = inv[idx].get('abv', 0)
            name = inv[idx].get('name')
            supplier = inv[idx].get('supplier')
            volume = inv[idx].get('volume', 0)
            ncount = count//abs(count)
            for i in range(abs(count)):
                new_ticket.append([idx, name, ncount, price, profit, is_intern,
                                   family, subfamily, pack, zrepdate,
                                   weekday, brewery, supplier, volume, abv])
        elif line[:2] == b' <':
            # add time, date, check sum
            ts = datetime.datetime.strptime(line[2:16].decode('latin-1'), '%d-%m-%y %H:%M')
            for x in new_ticket:
                x.append(ts)
            # if new_ticket:
            #     print(new_ticket)
            #     exit()
    transactions += new_ticket

prev_z = datetime.datetime.min
dirname = len(sys.argv) > 1 and sys.argv[1] or 'FICHEDTT/00010014_201'
for fname in sorted(glob(dirname + '*')):
    ts = datetime.datetime.min
    with open(fname, 'rb') as f:
        zrepdate = datetime.datetime.strptime(fname[-12:-4], '%Y%m%d')
        weekday = datetime.datetime.weekday(zrepdate)
        weekday = 6 if weekday == 0 else weekday - 1
        for line in f:
            if line.startswith(b'JOURNAL'):
                break
        ticket = []
        cancelled = False
        for line in f:
            # if line[:2] == b' <': # HACK FOR STUPID FAILING PRINTER
            #     already_registered = False
            #     ts = datetime.datetime.strptime(line[2:16].decode('latin-1'), '%d-%m-%y %H:%M')
            #     if ts <= prev_z:
            #         already_registered = True
            ticket.append(line)
#            if line[:6] == b"B   ":
#                cancelled = True # Ticket aborted
            if line[:2] == b" <":
                already_registered = False
                ts = datetime.datetime.strptime(line[2:16].decode('latin-1'), '%d-%m-%y %H:%M')
                if ts <= prev_z:
                    already_registered = True
                if not cancelled and not already_registered:
                    register(ticket, fname[-12:-4], weekday)
                cancelled = False
                ticket = []
    prev_z = ts

# Read varetelling
physical_counts = {}
for fname in sorted(glob('varetelling/*')):
    with open(fname) as f:
        dt = datetime.datetime.strptime(fname.split('/')[-1], '%Y-%m-%dT%H')
        physical_counts[dt] = {}
        for line in f:
            line = line.strip().split('\t')
            if len(line) == 3:
                physical_counts[dt][int(line[0])] = int(line[2])
pc = pd.DataFrame(physical_counts)
last_pc_time = pc.columns[-1]

# Read varemottak
goods_receipts = {}
for fname in glob('varemottak/*'):
    with open(fname) as f:
        dt = datetime.datetime.strptime(fname.split('/')[-1], '%Y-%m-%dT%H')
        goods_receipts[dt] = {}
        for line in f:
            line = line.strip().split('\t')
            if len(line) == 3:
                goods_receipts[dt][int(line[0])] = int(line[2])
gr = pd.DataFrame(goods_receipts).transpose()

stock = pc[last_pc_time]


invdf = pd.DataFrame(inv).transpose()
invdf['stock'] = stock.reindex_like(invdf).fillna(0)
invdf['stock'] += (gr[last_pc_time:]
                   .sum()
                   .transpose()
                   .reindex_like(invdf)
                   .fillna(0)
                   )
invdf['abv'].fillna(0, inplace=True)

def month(date):
    return date.month
def year(date):
    return date.year
def week(date):
    return date.week if not (date.month == 12 and date.week == 1) else 53
def pubtime(date):
    return date.hour if date.hour > 3 else 24 + date.hour
def halfhour(date):
    return int((pubtime(date) + (.5 if date.minute > 29 else 0))*10)
def quarter(date):
    return pubtime(date)*100 + 25 * (date.minute//15)
def minute(date):
    return pubtime(date)*100 + int(date.minute*10/6)
def price_intern(row, tr):
    if row.family == 0:
        if len(tr[(tr.idx == row.idx) & (tr.intern == True)]) > 4:
            return abs(tr[(tr.idx == row.idx) & (tr.intern == True)]['price'][-1])
def price_extern(row, tr):
    if row['price_extern'] > 0:
        return row.price_extern
    if row.family == 0:
        if len(tr[(tr.idx == row.idx) & (tr.intern == False)]) > 4:
            return abs(tr[(tr.idx == row.idx) & (tr.intern == False)]['price'][-1])


tr = pd.DataFrame(transactions, columns=('idx', 'name', 'count', 'price',
                                         'profit', 'intern', 'family', 'subfamily',
                                         'packaging', 'zreport',
                                         'weekday', 'brewery', 'supplier',
                                         'volume', 'abv', 'time'))
tr = tr.set_index(tr.time)
tr = tr.ix[:, ['idx', 'name', 'count', 'price', 'profit', 'intern', 'family',
               'subfamily', 'packaging', 'zreport', 'weekday',
               'brewery', 'supplier', 'volume', 'abv']]
#tr['count'].resample('30T', how='sum').plot('bar')
#tr['hour'] = tr.index.map(pubtime)
tr['quarter'] = tr.index.map(quarter)
tr['halfhour'] = tr.index.map(halfhour)
tr['week'] = tr.index.map(week)
tr['month'] = tr.index.map(month)
tr['year'] = tr.index.map(year)

# Subtract sales since last physical count (except kegs)
invdf['stock'] = (invdf['stock'] - tr[(tr.index > last_pc_time) &
                                      (tr.packaging != 2)].groupby('idx').sum()['count']
                .reindex_like(invdf['stock']).fillna(0))
# TODO Represent keg sales in stock

# For export to beer menu
invdf['idx'] = invdf.index
invdf['price_intern'] = invdf.apply(price_intern, 1, args=(tr,)).fillna(0)
invdf['price_extern'] = invdf.apply(price_extern, 1, args=(tr,)).fillna(0)
beers = invdf[(invdf.family == 0) | (invdf.subfamily == 8)].drop(['family', 'idx'], 1)
#print beers[beers.stock > 3].groupby(['subfamily', 'brewery', 'name',
#                                      'packaging', 'volume', 'price_intern', 'price_extern']).sum()

beerlist = list(beers[beers.stock > 3].groupby(['subfamily', 'brewery', 'name',
                                           'packaging', 'volume', 'price_intern',
                                                'price_extern', 'abv']).sum().transpose())
lastbeer = (-1, 0, 0, 0, 0, 0, 0)
of = open('menu.tex', 'w')
print(r"""\documentclass[norsk,10pt,a4paper]{article}
\usepackage[utf8]{inputenc}
\usepackage[T1]{fontenc}
\usepackage[norsk]{babel}
\usepackage[margin=1.5cm]{geometry}
\usepackage{multicol}
\usepackage{array}
\usepackage[compact]{titlesec}
\newcolumntype{L}[1]{>{\raggedright\let\newline
\\\arraybackslash\hspace{0pt}}m{#1}}
\newcolumntype{R}[1]{>{\raggedleft\let\newline
\\\arraybackslash\hspace{0pt}}m{#1}}
\titleformat{\subsubsection}{\normalfont\footnotesize\bfseries}{\S\,\thesection}{1em}{}
\titleformat{\section}{\normalfont\Large\bfseries}{\S\,\thesection}{1em}{}
\setlength{\textheight}{725pt}
\pagestyle{empty}
\begin{document}
\date{}
\title{\Huge{\textbf{ØL}}}
\maketitle
\vspace{-1cm}
\thispagestyle{empty}
\begin{multicols}{2}
""", file=of)
# print >> of, '\\begin{tabular}{L{.25\\textwidth}rrr}'
first = True
for beer in beerlist:
    newtype = beer[0] != lastbeer[0] or first
    newbrewery = beer[1] != lastbeer[1] or newtype or first
    if newtype:
        print('\\section*{%s}' % subfamilies[beer[0]], file=of)
    if newbrewery:
        if not first:
            print('\\end{tabular}', file=of)
        else:
            first = False
        print(('\\subsubsection*{%s}' % beer[1]).replace('&', r'\&'), file=of)
        print('\\begin{tabular}{L{.23\\textwidth}R{.06\\textwidth}R{.05\\textwidth}R{.05\\textwidth}}', file=of)
    print('%s %s & %s \\%% & %s l & %s \\\\' % (beer[2].replace('#',r'\#'), '(fat)' if beer[3] == 2 else '',
                                                         ('%.1f' % beer[7]).replace('.', ','),
                                                         ('%.2f' % beer[4]).replace('.', ','),
                                                         ('%d,–' % beer[6]) if beer[6] else ''), file=of)
    lastbeer = beer
print("""\\end{tabular}
\\end{multicols}
\\end{document}
""", file=of)
of.close()
# Plot autumn 13 vs autumn 14
# tr[tr.month > 6].groupby(['month', 'year']).sum()['price'].unstack(1).plot(kind='bar')

if dirname[-4:-1] == '.DT':
    print(tr.groupby('family').sum()['price'])
    exit(0)

def cmp_yr(idx):
    """Plot product count per month comparing years."""
    tr[tr.idx == idx].groupby(['month', 'year']).sum()['count']\
    .unstack(1).plot(kind='bar', title=inv[idx][0])

# spring14[spring14.idx == 61].groupby('week').sum()['count']

# print 2013
# print tr[tr.month > 7].groupby(['subfamily', 'year']).sum()['price']
# tr[tr.month > 7].groupby(['subfamily', 'year']).sum()['price'].unstack(1).plot(kind='bar')
# print (tr['2013-08-01':'2013-11-30']
#        .groupby('subfamily')
#        .sum()['price']
#        )
# print tr['2013-08-01':'2013-11-30'].groupby('packaging').sum()['price']
# print 2014
# print tr['2014-08-01':'2014-11-30'].groupby('subfamily').sum()['price']
# print tr['2014-08-01':'2014-11-30'].groupby('packaging').sum()['price']
# exit(0)

bar = tr.between_time('18:00', '01:59')

# Plot all friday revenue as a histogram
# fridays = bar[bar.weekday == 4].groupby('zreport').sum()['price']
# fridays.plot(kind='bar')

# Print z report for specific date
# print bar[bar.zreport == '20140125'].groupby('family').sum()['price']

# Histograms for pub nights
# (bar
#  .groupby(['halfhour',
#            'intern',
#        ])
#  .sum()['price']
#  .unstack(1)
#  .plot(kind='bar',
#        stacked=True,
#    )
#  )
# (bar
#  .groupby(['halfhour', 'family'])
#  .sum()['price']
#  .unstack(1)
#  .plot(kind='bar', stacked=True)
#  )
# (bar
# .groupby(['halfhour', 'subfamily'])
#  .sum()['price']
#  .unstack(1)
#  .plot(kind='bar', stacked=True)
#  )
# (bar
#  .groupby(['halfhour', 'packaging'])
#  .sum()['price']
#  .unstack(1)
#  .plot(kind='bar', stacked=True)
# )
 
cafe = tr.between_time('10:00', '15:59')

# cafe.groupby(['quarter', 'intern']).sum()['price'].unstack(1).plot(kind='bar', stacked=True)
# cafe.groupby(['quarter', 'family']).sum()['price'].unstack(1).plot(kind='bar', stacked=True)
