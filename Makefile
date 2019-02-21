.PHONY: clean clean-test clean-pyc clean-build re-clean-build clean-venv check-venv install-venv develop-venv help foo build re-build
.DEFAULT_GOAL := help

SHELL := /bin/bash
export VIRTUALENVWRAPPER_PYTHON := /usr/bin/python

define BROWSER_PYSCRIPT
import os, webbrowser, sys

try:
	from urllib import pathname2url
except:
	from urllib.request import pathname2url

webbrowser.open("file://" + pathname2url(os.path.abspath(sys.argv[1])))
endef
export BROWSER_PYSCRIPT

define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
	match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
	if match:
		target, help = match.groups()
		print("%-20s %s" % (target, help))
endef
export PRINT_HELP_PYSCRIPT

BROWSER := python -c "$$BROWSER_PYSCRIPT"

help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

check-venv: ## verify that the user is running in a Python virtual environment
	@if [ -z "$(VIRTUALENVWRAPPER_SCRIPT)" ]; then echo 'Python virtualenvwrapper not installed!' && exit 1; fi
	@if [ -z "$(VIRTUAL_ENV)" ]; then echo 'Not running within a virtual environment!' && exit 1; fi

clean: clean-test clean-pyc clean-build   ## remove all build, test, coverage, artifacts and wipe virtualenv

clean-build: ## remove build artifacts
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

re-clean-build: ## remove build artifacts
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

clean-pyc: ## remove Python file artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test: ## remove test and coverage artifacts
	rm -fr .tox/
	rm -f .coverage
	rm -fr htmlcov/
	rm -fr .pytest_cache/

clean-venv: check-venv ## remove all packages from current virtual environment
	@pip uninstall -y pytest-zigzag || echo "Skipping uninstall of pytest-zigzag or already uninstalled"
	@source virtualenvwrapper.sh && wipeenv || echo "Skipping wipe of environment"

lint: ## check style with flake8
	flake8 pytest_zigzag setup.py tests

test: ## run tests quickly with the default Python
	py.test

test-all: ## run tests on every Python version with tox
	tox

coverage-html: ## check code coverage with an HTML report
	py.test --cov-report html --cov=pytest_zigzag tests/
	$(BROWSER) htmlcov/index.html

coverage-term: ## check code coverage with a simple terminal report
	py.test --cov-report term-missing --cov=pytest_zigzag tests/

dist: clean ## builds source and wheel package
	python setup.py sdist
	python setup.py bdist_wheel
	ls -l dist

install: clean ## install the package to the active Python's site-packages
	python setup.py install

install-venv: clean-venv install ## install the package after wiping the virtual environment

develop: clean ## install necessary packages to setup a dev environment
	pip install -r requirements.txt
	pip install -e .

develop-venv: clean-venv develop ## setup a dev environment after wiping the virtual environment

publish: ## publish package to PyPI
	twine upload dist/*.whl

build: ## build a wheel
	python setup.py bdist_wheel

re-build: ## build a wheel
	python setup.py bdist_wheel

bump-major: ## bumps the major version
	bumpversion major

bump-minor: ## bumps the minor version
	bumpversion minor

bump-patch: ## bumps the patch version
	bumpversion patch

bump-build: ## bumps the build version
	bumpversion build

bump-release: ## prepares the version number for production release
	bumpversion --tag release

release-major: clean-build build develop lint test re-clean-build bump-major bump-release re-build publish ## package and upload a major release
	echo 'Successfully released!'
	echo 'Please push the newly created tag and commit to GitHub.'

release-minor: clean-build build develop lint test re-clean-build bump-minor bump-release re-build publish ## package and upload a minor release
	echo 'Successfully released!'
	echo 'Please push the newly created tag and commit to GitHub.'

release-patch: clean-build build develop lint test re-clean-build bump-patch bump-release re-build publish ## package and upload a patch release
	echo 'Successfully released!'
	echo 'Please push the newly created tag and commit to GitHub.'

release: clean-build build develop lint test re-clean-build bump-release re-build publish ## package and upload a patch release
	echo 'Successfully released!'
	echo 'Please push the newly created tag and commit to GitHub.'
