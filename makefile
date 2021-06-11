lint:
	flake8; \
	pylint clickable

test:
	nosetests

test-unit:
	nosetests unit

test-integration:
	nosetests integration
