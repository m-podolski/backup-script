.PHONY: run test

run:
	poetry run python3 -m app.main

test:
	poetry run python3 -m pytest \
		-v \
		--cov=app \
		--cov-report=term \
		--cov-report=html:coverage-report \
		tests/
