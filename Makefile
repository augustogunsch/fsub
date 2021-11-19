dist: setup.cfg pyproject.toml
	rm -rfv src/fsub.egg-info
	rm -rfv dist
	python3 -m build

upload: dist
	python3 -m twine upload --repository pypi dist/*

check:
	python3 -m unittest tests

clean:
	rm -rfv tests/__pycache__
	rm -rfv src/fsub/__pycache__
