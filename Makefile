browser:
	@$@

.PHONY: build
build:  # run: write, docs, clean and venv (requirements)
	@$@

builds:  # run: write, docs, clean and venv (requirements)
	@$@

clean:
	@$@

commit: tests
	@$@

completions:
	@$@

coverage:
	@proj $@

.PHONY: docs
docs:
	@$@

latest:
	@$@

next:
	@$@

nodeps:
	@python3 -m pip install --upgrade -q $@[all,dev]

publish:  # runs: docs, tests (build (clean, venv (requirements)), pytest, ruff & tox), commit, tag, push, twine & clean
	@$@

pyenv:
	@pyenv install 3.11
	@pyenv install 3.12-dev

pytest:
	@proj $@

pytests:
	@$@

requirement:
	@$@ --install

requirements:
	@$@

ruff:
	@proj $@

secrets:
	@$@

test:
	@proj $@

.PHONY: tests
tests:  # runs: build (clean, venv (requirements)), pytest, ruff and tox
	@$@

tox:
	@proj $@

twine:
	@proj $@

.PHONY: venv
venv:  # runs: requirements
	@$@

venvs:  # runs: requirements
	@$@

.DEFAULT_GOAL := publish
