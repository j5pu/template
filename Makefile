.PHONY: docs tests venv

browser:
	@$@

build:  # run: write, docs, clean and venv (requirements)
	@$@

clean:
	@$@

commit: tests
	@$@

completions:
	@$@

coverage:
	@proj $@

docs:
	@$@

latest:
	@$@

next:
	@$@

pproj:
	@python3 -m pip install --upgrade -q $@

publish:  # runs: docs, tests (build (clean, venv (requirements)), pytest, ruff & tox), commit, tag, push, twine & clean
	@$@

pyenv:
	@pyenv install 3.11
	@pyenv install 3.12-dev

pytest:
	@proj $@

requirements:
	@$@ --install

ruff:
	@proj $@

secrets:
	@$@

tests:  # runs: build (clean, venv (requirements)), pytest, ruff and tox
	@$@

tox:
	@proj $@

twine:
	@proj $@

venv:  # runs: requirements
	@$@

.DEFAULT_GOAL := publish
