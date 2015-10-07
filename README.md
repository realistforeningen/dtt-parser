# DTT-parser

## Import existing data

Acquire the lates source files (`zrep.tar.xz`). Uncompress it from this
directory:

```
$ cd dtt-parser
$ tar -xf ~/Downloads/zrep.tar.xz
```

## Import new files

1. Put the files into `sources/`
2. Run `make`
3. `archives/all.tar.xz` contains everything. Back this up somewhere.

## Build reports

**Step 1:** Run `make latest` to find the latest transaction that is included in the DTT files.

**Step 2:** Append that timestamp to the `reports.txt`-file:

```
2015-08-31 19:10
2015-09-14 12:00
2015-10-14 12:00
```

**Step 3:** Run `make`.

**Step 4:** `reports/001.txt` and `reports/002.txt` now contains the data for
the two time periods.

**Step 5:** (*On Mac*) Write `pbcopy < reports/002.txt` to copy the data to the
clipboard. Paste it into Google Sheets.

## When in doubt

Run `make`.

