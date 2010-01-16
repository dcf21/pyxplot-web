all: astrolabe.pdf

astrolabe.pdf: astrolabe.ps
	ps2pdf astrolabe.ps astrolabe.pdf

astrolabe.ps: astrolabe.dvi
	dvips astrolabe.dvi -o astrolabe.ps

astrolabe.dvi: astrolabe.tex mother_back.eps plate.eps rete.eps rule.eps
	latex astrolabe.tex

rete.eps: rete.ppl bright_stars.out rete_text.dat
	../../pyxplot8/bin/pyxplot rete.ppl

bright_stars.out: bright_stars.py bright_stars.dat bright_star_names.dat
	python bright_stars.py

rete_text.dat: rete_text.py
	python rete_text.py

rule.eps: rule.ppl
	../../pyxplot8/bin/pyxplot rule.ppl

plate.eps: plate.ppl
	../../pyxplot8/bin/pyxplot plate.ppl

mother_back.eps: mother.ppl mother_back_text.dat
	../../pyxplot8/bin/pyxplot mother.ppl

mother_back_text.dat: mother_back_text.py
	python mother_back_text.py

clean:
	rm mother_back_text.dat bright_stars.out *.eps *.ps *.dvi *.aux *.log *.pdf
