.PHONY: build doctor test examples docs serve shell

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
