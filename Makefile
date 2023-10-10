brew:
	@p $@

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
	@p $@

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

push:
	@rm -f docs/conf.py docs/requirements.txt docs/reference.md
	@git add .
	@git commit --quiet -a -m "$${msg:-fix}" || true
	@git tag $$(svu next --strip-prefix)
	@git push --quiet --tags
	@git push --quiet

pyenv:
	@pyenv install 3.11
	@pyenv install 3.12-dev

pytest:
	@p $@

pytests:
	@$@

requirement:
	@$@ --install

requirements:
	@$@

ruff:
	@p $@

secrets:
	@$@

test:
	@p $@

.PHONY: tests
tests:  # runs: build (clean, venv (requirements)), pytest, ruff and tox
	@$@

tox:
	@p $@

twine:
	@p $@

.PHONY: venv
venv:  # runs: requirements
	@$@

venvs:  # runs: requirements
	@$@

write:
	@p $@

.DEFAULT_GOAL := publish
