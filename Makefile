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
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf reports/
	rm -rf .tox/

poetry:
	cat requirements.txt | grep -E '^[^# ]' | cut -d= -f1 | xargs -n 1 poetry add

checkos:
	@echo $(OS_NAME)

dist: clean
	python setup.py sdist
	#python setup.py bdist_wheel
	ls -lh dist

lint:
	@pylint -r y service
# 	isort --recursive .
# 	flake8 service tests
# 	pycodestyle --ignore=E501,F403,E122 **/*.py

fmt:
	black -l 120 -t py36 -t py37 -t py38 -t py39 -t py310 .

dep:
	python -m pip install -r requirements.txt

pip:
	pip-compile requirements.in --no-emit-index-url

cov: # pytest cov
	poetry run pytest tests --cov=service --cov-report=html -v

#test:
## 	DJANGO_SETTINGS_MODULE=config.settings.test poetry run python manage.py test tests --parallel --traceback
##	DJANGO_SETTINGS_MODULE=config.settings.prd poetry run python manage.py test tests --traceback -v2 $(OPT)
#	poetry run pytest tests -vv $(TEST_OPT)

test:
	DJANGO_SETTINGS_MODULE=config.settings.test poetry run python manage.py test tests --traceback -v2


start: ## 运行全部服务
	poetry run honcho start

shell:
	DJANGO_SETTINGS_MODULE=config.settings.dev poetry run python manage.py shell_plus

requirements:
	poetry export --without-hashes --without-urls --with=main --with=prd -o requirements.txt
	#poetry export --without-hashes --with=main --with=prd --with=prometheus --with=celery --without-urls -o requirements.txt
#ifeq ($(OS_NAME), Darwin)
#	sed -i '' '/meinheld/,+0d' requirements.txt
#	sed -i '' '/greenlet/,+0d' requirements.txt
#endif
#ifeq ($(OS_NAME), Linux)
#	sed -i '/meinheld/,+0d' requirements.txt
#	sed -i '/greenlet/,+0d' requirements.txt
#endif

docker: requirements ## 编译 docker 镜像
	# pip install -U docker-squash

	docker build . -f deployments/compose/postgres/Dockerfile -t postgres:habit
	docker build . -f deployments/compose/django/Dockerfile -t habit:onbuild --build-arg VERSION="$(VERSION)"

	docker-squash habit:onbuild -t habit:squash
	docker build . -t habit:$(VERSION)

	docker rmi habit:squash
	docker image list

#compose:
#	docker compose run --volume `pwd`/service:/app/service --rm server python3 manage.py migrate
#	docker compose run --volume `pwd`:/app --rm server python3 manage.py habittatic --no-input
#	docker compose run --rm server python3 manage.py createsuperuser --username=bopo --email=ibopo@126.com
#	#docker compose run --volume `pwd`/scripts:/app/scripts --rm server python3 manage.py runscript expross -v2
#	#docker compose run --volume `pwd`/scripts:/app/scripts --rm server python3 manage.py runscript area -v2
#	docker compose up -d


schedule:
	poetry run python schedule.py

queue:
	DJANGO_SETTINGS_MODULE=config.settings.dev poetry run python manage.py qcluster -v2 --traceback

dev:
	DJANGO_SETTINGS_MODULE=config.settings.dev poetry run python manage.py runserver 0.0.0.0:8000

prd:
	DJANGO_WHITENOISE_ENABLE=1 DJANGO_SETTINGS_MODULE=config.settings.prd poetry run python manage.py runserver 0.0.0.0:8000

deploy: # 部署项目
	echo deploy

migrate:
	DJANGO_SETTINGS_MODULE=config.settings.$(MODE) poetry run python manage.py makemigrations
	DJANGO_SETTINGS_MODULE=config.settings.$(MODE) poetry run python manage.py migrate

upgrade: migrate ## 升级项目, 使用变量 MODE 作为参数 (例如: `make upgrade MODE=pro`)
	DJANGO_SETTINGS_MODULE=config.settings.$(MODE) poetry run python manage.py loaddata assets/fixtures/*.json

static:
	fab collect
	#DJANGO_WHITENOISE_ENABLE=0 DJANGO_DATABASE_DRIVER=sqlite3 DJANGO_SETTINGS_MODULE=config.settings.prd poetry run python manage.py collectstatic --no-input

locale:
	DJANGO_SETTINGS_MODULE=config.settings.$(MODE) poetry run python manage.py compilemessages -l zh_Hans

fixture:
	poetry run python manage.py loaddata assets/fixtures/user.json
	poetry run python manage.py habittatic --noinput

prepare: ## 准备开发环境
	git config user.email ibopo@126.com
	git config pull.rebase false
	git config user.name bopo
	poetry install --sync

cleanup: ## 清理开发环境
	@poetry env remove `poetry env list | grep '(Activated)' | cut -d ' ' -f1 | sed 's/-py/ /g' | awk '{print $$NF}'`

archive: checkos ## 项目归档
	git archive --format zip --output ../archive/server_$(BRANCH)_$(shell date +'%Y_%m_%dT%H_%M_%S').zip $(BRANCH)
	ls -lht ../archive

coverage:
	coverage report -m
	coverage html
	$(BROWSER) htmlcov/index.html

compose: package requirements
	cp deployments/environ/env.docker2 .env
	docker compose build

backup: ## 创建数据库备份
	docker compose exec postgres backup

backups: checkos ## 数据库备份复制到宿主机
	@docker compose exec postgres backups
	@docker cp `docker compose ps -q postgres`:/backups ./backups

restore: ## 恢复数据库(例: `make restore TAR=backup_2023_02_01T09_53_58.sql.gz`)
	docker compose exec postgres restore $(TAR)

compile:
	mkdir -p dist
	cp docker-compose.yaml dist/docker-compose.yml
	cp install.sh dist/install.sh
	docker save habit:$(VERSION) -o dist/habit-$(VERSION).tar.gz

	ls -lht dist

package: ## 项目打包
	rm -rf build
	mkdir -p dist target build/assets build/fixtures build/docker
#	fab package

	cp -R assets/static build/assets/static
	cp -R assets/fixtures/*.json build/fixtures

	cp docker-compose.yaml build/docker-compose.yml
	cp deployments/environ/env.docker build/env.docker

	#mkdir -p build/deployments/compose
	#cp -R deployments/compose/postgres build/deployments/compose/

	docker save habit:$(VERSION) -o build/docker/habit-$(VERSION).tar.gz
	shasum ./build/docker/habit-$(VERSION).tar.gz >./build/docker/habit-$(VERSION).tar.gz.md5

	docker save postgres:habit -o build/docker/postgres-$(VERSION).tar.gz
	shasum ./build/docker/postgres-$(VERSION).tar.gz >./build/docker/postgres-$(VERSION).tar.gz.md5

	tar zcfv ./dist/habit-$(VERSION).tar.gz build/
	ls -lht ./dist

release: package ## 项目发布打包


bump:
	cz bump --yes -ch -cc --increment patch

# DO NOT DELETE
