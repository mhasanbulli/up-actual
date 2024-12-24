## format, lint and type check
check: export SKIP=test
check: hooks

## format and lint
format: export SKIP=pyright,test
format: hooks

## pyright type check
pyright: $(venv)
	uv run pyright

## run tests
test: $(venv) 
	PYTHONPATH=$(PYTHONPATH) uv run pytest