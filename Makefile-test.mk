## format, lint and type check
check: export SKIP=test
check: hooks

## format and lint
format: export SKIP=pyright,test
format: hooks

## pyright type check
pyright: 
	uv run pyright

## run tests
test:
	PYTHONPATH=$(PYTHONPATH) uv run pytest -m "not integration"

test-all:
	PYTHONPATH=$(PYTHONPATH) uv run pytest
