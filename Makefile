.PHONY: clean publish tests version

msg := rm if empty path
SHELL := $(shell bash -c 'command -v bash')
ROOT_DIR:=$(shell dirname $(realpath $(firstword $(MAKEFILE_LIST))))
PYTHONPATH := $(ROOT_DIR)/src
export msg
export PYTHONPATH

build: clean
	@source venv/bin/activate && python3 -m build --wheel

clean:
	@rm -rf build dist **/*.egg-info *.egg-info .mypy_cache .pytest_cache .tox **/scanned_*.pdf **/generated_*.pdf \
		src/pdf/data/Reembolsos

commit: tests tox
	@git add .
	@git commit --quiet -a -m "$${msg:-fix}" || true
	@git push --quiet

coverage:
	@source venv/bin/activate && coverage run -m pytest && coverage report


publish: commit
	@source venv/bin/activate && twine upload -u __token__ dist/*
	@make clean


requirements:
	@test -d venv || python3.11 -m venv venv
	@source venv/bin/activate && pip3 install --upgrade pip pip-tools && \
		pip-compile --all-extras --no-annotate --quiet -o /tmp/requirements.txt pyproject.toml && \
		pip3 install -r /tmp/requirements.txt

tests: clean build
	@source venv/bin/activate && pytest

tox:
	@eval "$$(pyenv init --path)"; source venv/bin/activate && PY_IGNORE_IMPORTMISMATCH=1 tox

pyenv:
	@pyenv install 3.10
	@pyenv install 3.11
	@pyenv install 3.12-dev
