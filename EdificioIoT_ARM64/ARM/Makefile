procesador: procesador.o
	ld -o procesador procesador.o

procesador.o: procesador.s
	as -g -o procesador.o procesador.s

clean:
	rm -f procesador procesador.o resultado.txt

.PHONY: clean