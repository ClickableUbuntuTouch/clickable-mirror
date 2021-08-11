lint:
	flake8; \
	pylint clickable

format:
	autopep8 --in-place --recursive --aggressive clickable
	autopep8 --in-place --recursive --aggressive tests

test:
	pytest --cov=clickable ./tests

test-unit:
	pytest --cov=clickable ./tests/unit

test-integration:
	pytest --cov=clickable ./tests/integration
