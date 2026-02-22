MAKEFLAGS += --warn-undefined-variables --check-symlink-times
SHELL = /bin/bash -o pipefail
.DEFAULT_GOAL := help
.PHONY: help clean install format check pyright test hooks install-hooks
PYTHONPATH=$(shell pwd)

## display help message
help:
	@awk '/^##.*$$/,/^[~\/\.0-9a-zA-Z_-]+:/' $(MAKEFILE_LIST) | awk '!(NR%2){print $$0p}{p=$$0}' | awk 'BEGIN {FS = ":.*?##"}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}' | sort

.uv:
	@uv --version || { echo 'Please install uv: https://docs.astral.sh/uv/getting-started/installation/' && exit 13 ;}

.sync:
	uv sync

## delete the venv
clean:
	rm -rf .venv

## create venv and install this package and hooks
install: .uv .sync $(if $(value CI),,install-hooks)


install-hooks: .git/hooks/pre-push

.git/hooks/pre-push:
	uv run pre-commit install --install-hooks -t pre-push

## run pre-commit git hooks on all files
hooks:
	uv run pre-commit run --color=always --all-files --hook-stage push
