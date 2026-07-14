.PHONY: build doctor test examples docs serve shell \
        report report-watch report-serve report-clean

build:
	./claw-spice build

doctor:
	./claw-spice doctor

test:
	./claw-spice test

examples:
	./claw-spice examples run

docs:
	./claw-spice docs build

serve:
	./claw-spice docs serve

shell:
	./claw-spice shell

SLUG ?= lab-01

report:
	./claw-spice report

report-watch:
	./claw-spice report watch $(SLUG)

report-serve:
	./claw-spice report serve $(SLUG)

report-clean:
	./claw-spice report clean
