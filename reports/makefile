TEX= latex -shell-escape

NAME=report
SRC= $(NAME).tex
PDF= $(NAME).pdf

$(PDF): $(SRC)
	$(TEX) -output-format=pdf $(SRC)

.PHONY: clean
clean:
	rm $(NAME).aux $(NAME).log $(NAME).stderr $(NAME).stdout $(NAME).sh wordcount

