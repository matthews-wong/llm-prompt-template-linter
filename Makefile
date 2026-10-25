.PHONY: validate test lint

validate: test lint

test:
	python3 -m unittest discover -s tests

lint:
	python3 -m promptlint prompts/
