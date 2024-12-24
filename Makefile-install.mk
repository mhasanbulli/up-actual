MAKEFLAGS += --warn-undefined-variables --check-symlink-times
SHELL = /bin/bash -o pipefail
.DEFAULT_GOAL := help
.PHONY: help clean install format check pyright test hooks install-hooks
PYTHONPATH=$(shell pwd)

## display help message
help:
	@awk '/^##.*$$/,/^[~\/\.0-9a-zA-Z_-]+:/' $(MAKEFILE_LIST) | awk '!(NR%2){print $$0p}{p=$$0}' | awk 'BEGIN {FS = ":.*?##"}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}' | sort

venv ?= .venv

$(venv): pyproject.toml
	uv venv
	touch $(venv)

# delete the venv
clean:
	rm -rf $(venv)

## create venv and install this package and hooks
install: $(venv) install-hooks
	uv sync
	touch $(venv)

## run pre-commit git hooks on all files
hooks: $(venv)
	uvx pre-commit run --color=always --all-files --hook-stage push

install-hooks: .git/hooks/pre-push

.git/hooks/pre-push: $(venv)
	uvx pre-commit install --install-hooks -t pre-push
