.PHONY: clean publish tests version

msg := fix: $(shell git status --porcelain | grep -v "^??" | cut -c4- | tr '\n' ' ')
SHELL := $(shell bash -c 'command -v bash')
ROOT_DIR:=$(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))
PYTHONPATH := $(ROOT_DIR)/src
export msg
export PYTHONPATH

brew:
	@brew bundle --file=src/huti/data/Brewfile --no-lock --quiet

build: clean
	@{ [ "$${CI-}" ] || source venv/bin/activate; } && python3 -m build --wheel

clean:
	@sudo rm -rf build dist **/*.egg-info *.egg-info .mypy_cache .pytest_cache .tox **/scanned_*.pdf **/generated_*.pdf \
		src/pdf/data/Reembolsos ./huti-*  .coverage .ruff_cache

commit: tests tox
	@git add -A .
	@git commit --quiet -a -m "$${msg:-fix:}" || true

coverage:
	@{ [ "$${CI-}" ] || source venv/bin/activate; } && coverage run -m pytest && coverage report

lint:
	@{ [ "$${CI-}" ] || source venv/bin/activate; } && ruff check src

publish: tag
	@make build
	@{ [ "$${CI-}" ] || source venv/bin/activate; } && twine upload -u __token__ dist/*
	@git push --tags --quiet || true
	@make clean


requirements:
	@{ [ "$${CI-}" ] || source venv/bin/activate; } && test -d venv || python3.11 -m venv venv
	@venv/bin/python -c "from huti.cli.dependencies import dependencies; dependencies()"
#	@{ [ "$${CI-}" ] || source venv/bin/activate; } && python3 -m pip install --upgrade pip pip-tools && \
#		pip-compile --all-extras --no-annotate --quiet -o /tmp/requirements.txt pyproject.toml && \
#		python3 -m pip  install -r /tmp/requirements.txt

tag: commit
	@NEXT=$$(svu next --strip-prefix) && \
		CURRENT=$$(svu --strip-prefix) && \
		TAG=$$(git tag --list --sort=-v:refname | head -n1) && \
		{ test $$NEXT != $$CURRENT || test $$NEXT != $$TAG; } && \
		CHANGED=1 && echo $$CURRENT $$NEXT $$TAG && \
		git tag $$NEXT && \
		git push --quiet --tags  || true

pyenv:
	@pyenv install 3.10
	@pyenv install 3.11
	@pyenv install 3.12-dev

secrets:
	@gh secret set GH_TOKEN --body "$$GITHUB_TOKEN"
	@grep -v GITHUB_ /Users/j5pu/secrets/profile.d/secrets.sh > /tmp/secrets
	@gh secret set -f  /tmp/secrets

tests: lint build
	@{ [ "$${CI-}" ] || source venv/bin/activate; } && pytest

tox:
	@eval "$$(pyenv init --path)";{  [ "$${CI-}" ] || source venv/bin/activate; } && \
		PY_IGNORE_IMPORTMISMATCH=1 tox -p auto
