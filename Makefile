ROOT := $(shell git rev-parse --show-toplevel)
MAKEFLAGS += -j2

.PHONY: py-install npm-install generate-protos generate test test-py build-web-packages test-ts-api test-ts

start-local-pg:
	@scripts/local-pg.sh

py-install:
	uv --directory server sync

npm-install:
	cd web && npm install

generate-protos: py-install npm-install
	@scripts/gen_protos.sh

generate: generate-protos

test-py:
	uv --directory server run pytest

new-migration: start-local-pg
	uv --directory server run alembic revision --autogenerate -m "init tables"

migration-new:
ifndef MNAME
	$(error MSG is not set. Please run: make new-migration MNAME="migration name")
endif
	uv --directory server run alembic revision --autogenerate -m "$(MNAME)"

migration-apply:
	uv --directory server run alembic upgrade head

dev-server:
	@cd server && uv run scripts/dev/main.py

local-server: start-local-pg
	@cd server && uv run scripts/local/main.py

build-web-packages: web/packages/api/package.json
	@cd web/packages/api && npm run build

build-web-app: web/apps/dev-observer/package.json
	@cd web/apps/dev-observer && npm run build

dev-web: npm-install build-web-packages
	@scripts/dev-web.sh

local-compose:
	@scripts/compose-up.sh

test-ts-api:
	@cd web/packages/api && npm run test

test-ts: test-ts-api
	# ts tests executed

test: test-ts test-py
	# all tests executed

build: build-web-app
 # web is built


