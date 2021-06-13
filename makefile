lint:
	flake8; \
	pylint clickable

format:
	autopep8 --in-place --recursive --aggressive clickable
	autopep8 --in-place --recursive --aggressive tests

test:
	nosetests

test-unit:
	nosetests unit

test-integration:
	nosetests integration
