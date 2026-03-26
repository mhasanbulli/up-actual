## format, lint and type check
check: export SKIP=test
check: hooks

## format and lint
format: export SKIP=ty,test
format: hooks

## type check
tv:
	uv run ty check

## run tests
test:
	PYTHONPATH=$(PYTHONPATH) uv run pytest -m "not (schema or integration)"

test-all:
	PYTHONPATH=$(PYTHONPATH) uv run pytest
