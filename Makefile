.PHONY: all check latest

all: check reports archives/all.tar.xz

archives:
	mkdir -p $@

archives/all.tar.xz: sources | archives
	tar -cJf $@ $</*

ifneq ("$(wildcard reports.txt)", "")
reports: reports.txt sources parser.py
	mkdir -p reports
	rm -f reports/*
	python parser.py
else
reports:
endif

check:

latest:
	@ python latest.py

