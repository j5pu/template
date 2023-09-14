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
	@rm -rf build dist **/*.egg-info *.egg-info .mypy_cache .pytest_cache .tox **/scanned_*.pdf **/generated_*.pdf \
		src/pdf/data/Reembolsos ./huti-*  .coverage

commit: tests tox
	@git add .
	@git commit --quiet -a -m "$${msg:-fix:}" || true
	@git push --quiet --tags

coverage:
	@{ [ "$${CI-}" ] || source venv/bin/activate; } && coverage run -m pytest && coverage report


publish: commit
	@{ [ "$${CI-}" ] || source venv/bin/activate; } && twine upload -u __token__ dist/*
	@make clean


requirements:
	@{ [ "$${CI-}" ] || source venv/bin/activate; } && test -d venv || python3.11 -m venv venv
	@{ [ "$${CI-}" ] || source venv/bin/activate; } && python3 -m pip install --upgrade pip pip-tools && \
		pip-compile --all-extras --no-annotate --quiet -o /tmp/requirements.txt pyproject.toml && \
		python3 -m pip  install -r /tmp/requirements.txt

tests: build
	@{ [ "$${CI-}" ] || source venv/bin/activate; } && pytest

tox:
	@eval "$$(pyenv init --path)";{  [ "$${CI-}" ] || source venv/bin/activate; } && PY_IGNORE_IMPORTMISMATCH=1 tox

pyenv:
	@pyenv install 3.10
	@pyenv install 3.11
	@pyenv install 3.12-dev
