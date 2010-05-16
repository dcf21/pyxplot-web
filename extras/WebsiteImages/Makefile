# Makefile
# $Id$

PYXPLOT = ../../pyxplot8/bin/pyxplot

all: output/ex_euclid_I_47.jpg output/ex_fft.jpg output/ex_hrdiagram.jpg

output/%.jpg: %.ppl $(PYXPLOT)
	mkdir -p output
	$(PYXPLOT) $<

