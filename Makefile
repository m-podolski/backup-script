.PHONY: test

test:
	poetry run python3 -m pytest \
		-v \
		--cov=app \
		--cov-report=term \
		--cov-report=html:coverage-report \
		tests/
