# Makefile
# $Id$

PYXPLOT = ../../pyxplot8/bin/pyxplot

all: output/ex_blackbodies.png output/ex_euclid_I_47.png output/ex_fft.png output/ex_hrdiagram.png

output/%.png: %.ppl fig_init.ppl $(PYXPLOT)
	mkdir -p output
	$(PYXPLOT) $<

