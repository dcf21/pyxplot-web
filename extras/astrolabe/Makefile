all: astrolabe.pdf

astrolabe.pdf: astrolabe.ps
	ps2pdf astrolabe.ps astrolabe.pdf

astrolabe.ps: astrolabe.dvi
	dvips astrolabe.dvi -o astrolabe.ps

astrolabe.dvi: astrolabe.tex mother_back.eps plate.eps rete.eps
	latex astrolabe.tex

rete.eps: rete.ppl
	../../pyxplot8/bin/pyxplot rete.ppl

plate.eps: plate.ppl
	../../pyxplot8/bin/pyxplot plate.ppl

mother_back.eps: mother.ppl mother_back_text.dat
	../../pyxplot8/bin/pyxplot mother.ppl

mother_back_text.dat: mother_back_text.py
	python mother_back_text.py

clean:
	rm mother_back_text.dat *.eps *.ps *.dvi *.aux *.log *.pdf
