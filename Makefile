.PHONY: all check

all: check reports archives/all.tar.xz

archives:
	mkdir -p $@

archives/all.tar.xz: sources | archives
	tar -cJf $@ $</*

reports: reports.txt sources parser.py
	mkdir -p reports
	rm -f reports/*
	python parser.py

check:

