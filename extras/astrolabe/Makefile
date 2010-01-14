all: mother_back.eps plate.eps

plate.eps: plate.ppl
	../../pyxplot8/bin/pyxplot plate.ppl

mother_back.eps: mother.ppl mother_back_text.dat
	../../pyxplot8/bin/pyxplot mother.ppl

mother_back_text.dat: mother_back_text.py
	python mother_back_text.py

clean:
	rm mother_back_text.dat *.eps *.pdf
