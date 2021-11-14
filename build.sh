#!/bin/sh
rm -rv dist
python3 -m build

# Upload to PyPI with:
# python3 -m twine upload --repository pypi dist/*
