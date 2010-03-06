all: astrolabe.pdf astrolabe2.pdf

astrolabe.pdf: astrolabe.ps
	ps2pdf astrolabe.ps  astrolabe.pdf

astrolabe2.pdf: astrolabe2.ps
	ps2pdf astrolabe2.ps astrolabe2.pdf

astrolabe.ps: astrolabe.dvi
	dvips astrolabe.dvi  -o astrolabe.ps

astrolabe2.ps: astrolabe2.dvi
	dvips astrolabe2.dvi -o astrolabe2.ps

astrolabe.dvi: astrolabe.tex output/mother_back_simple.eps output/rete.eps output/rule.eps
	latex astrolabe.tex
	latex astrolabe.tex
	latex astrolabe.tex

astrolabe2.dvi: astrolabe2.tex output/mother_back.eps output/plate.eps output/rete.eps output/rule.eps
	latex astrolabe2.tex
	latex astrolabe2.tex
	latex astrolabe2.tex

output/rete.eps: rete.ppl bright_stars.out rete_text.dat
	../../pyxplot8/bin/pyxplot rete.ppl

bright_stars.out: bright_stars.py bright_stars.dat bright_star_names.dat
	python bright_stars.py

rete_text.dat: rete_text.py
	python rete_text.py

output/rule.eps: rule.ppl
	../../pyxplot8/bin/pyxplot rule.ppl

output/plate.eps: plate.ppl
	../../pyxplot8/bin/pyxplot plate.ppl

output/mother_back_simple.eps: mother_simple.ppl mother_back_text.dat
	../../pyxplot8/bin/pyxplot mother_simple.ppl

output/mother_back.eps: mother.ppl mother_back_text.dat
	../../pyxplot8/bin/pyxplot mother.ppl

mother_back_text.dat: mother_back_text.py
	python mother_back_text.py

clean:
	rm -Rf mother_back_text.dat mother_back_text_simple.dat mother_front_text_simple.dat plate_text_simple.dat rete_text.dat bright_stars.out output *.ps *.dvi *.aux *.log *.pdf
