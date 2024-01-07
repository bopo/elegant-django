# Makefile six
.PHONY: clean clean-test clean-pyc clean-build docs help tests test
.DEFAULT_GOAL := help
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
		dist, help = match.groups()
		print("%-20s %s" % (dist, help))
endef
export PRINT_HELP_PYSCRIPT

BRANCH = $(shell git rev-parse --abbrev-ref HEAD)
OS_NAME = $(shell uname -s)
LC_OS_NAME = $(shell echo $(OS_NAME) | tr '[A-Z]' '[a-z]')

ifndef ($(MODE))
	MODE=dev
endif

BROWSER := python -c "$$BROWSER_PYSCRIPT"
VERSION := 0.3.12

help:
	@python -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)


distclean: clean
	rm -rf fixture tests Procfile pytest.ini Vagrantfile requirements requirements.* env.* db.sqlite3 Pipfile *.md *.py
	find service -type f -name "[0-9]*.py" | xargs rm -rf
	rm -rf .pytest_cache
	rm -rf .vagrant
	rm -rf scripts
	rm -rf deployments
	rm -rf setup.*
	rm -rf *.yaml *.toml *.lock

clean: clean-build clean-others clean-test clean-pyc ## 清理各种编译和临时文件

clean-migrate:
	find . -type d -name migrations -exec find {} -name "[0-9]*.py" \; | egrep -v '__init__.py' | xargs rm
	#find service -type f -name "[0-9]*.py" | xargs rm -rf
	#find . -type d -name migrations -exec find {} -name "[0-9]*.py" \;

clean-build:
	rm -fr .pytest_cache/
	rm -fr dist/
	rm -fr build/
	rm -fr target/
	rm -fr .eggs/
	rm -fr .deploy
	rm -rf '*.tgz'

	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +
	find . -name '*.log' -exec rm -f {} +
	find . -name '*.sql' -exec rm -f {} +

clean-others:
	rm -fr runtime/**/**
	rm -rf celerybeat-schedule
	rm -rf dump.rdb
	rm -rf deploy/.fabric

	find . -name 'Thumbs.db' -exec rm -f {} +
	find . -name '*.tgz' -exec rm -f {} +
	find . -name 'dump.rdb' -exec rm -f {} +
	find . -name 'celery*.db' -exec rm -f {} +

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test:
	rm -rf nosetests.html
	rm -rf .hypothesis
	rm -rf .ruff_cache
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf reports/
	rm -rf .tox/

dist: clean
	poetry build
	ls -lh dist

pull:
	git pull origin `git symbolic-ref --short -q HEAD` --tags
	git pull github `git symbolic-ref --short -q HEAD` --tags

sync: pull
	git push origin `git symbolic-ref --short -q HEAD` --tags
	git push github `git symbolic-ref --short -q HEAD` --tags

lint:
	ruff check ./elegant

cov: # pytest cov
	poetry run pytest tests --cov=service --cov-report=html -v

test:
	DJANGO_SETTINGS_MODULE=tests.settings poetry run python manage.py test tests --traceback -v2

prepare: ## 准备开发环境
	git config user.email ibopo@126.com
	git config pull.rebase false
	git config user.name bopo

remove: ## 清理开发环境
	@poetry env remove `poetry env list | grep '(Activated)' | cut -d ' ' -f1 | sed 's/-py/ /g' | awk '{print $$NF}'`

publish: clean ## 项目发布打包
	poetry publish --build

# DO NOT DELETE
