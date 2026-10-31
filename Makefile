# Root Makefile for FloodFill-Micromouse project
.PHONY: all test test-c test-py run clean asan

all:
	$(MAKE) -C floodfill_c all

test: test-c test-py

test-c:
	$(MAKE) -C floodfill_c test

test-py:
	python3 -m unittest discover -s tests

run:
	$(MAKE) -C floodfill_c run

asan:
	$(MAKE) -C floodfill_c asan

clean:
	$(MAKE) -C floodfill_c clean

