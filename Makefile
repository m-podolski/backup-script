.PHONY: run test

run:
	poetry run python3 -m app.main

run-bu:
	poetry run python3 -m app.main backup

run-bu-pa:
	poetry run python3 -m app.main backup --source /path

test:
	poetry run python3 -m pytest \
		-v \
		--cov=app \
		--cov-report=term \
		--cov-report=html:coverage-report \
		tests/
