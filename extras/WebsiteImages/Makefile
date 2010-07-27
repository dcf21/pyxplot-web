# Makefile
# $Id$

PYXPLOT = ../../pyxplot8/bin/pyxplot

all: output/ex_blackbodies.png output/ex_branchcut.png output/ex_cornu.png output/ex_euclid_I_47.png output/ex_fft.png output/ex_hrdiagram.png output/ex_surface_contours.png output/ex_triangles.png

output/%.png: %.ppl fig_init.ppl $(PYXPLOT)
	mkdir -p output
	$(PYXPLOT) $<

