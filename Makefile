.DEFAULT_GOAL := help

ENV_DIR=env


# terminal colors config
NO_COLOR=\033[0m
OK_COLOR=\033[32;01m

.PHONY: lint deps generate help env setup

## lint: run lint via pylint
lint:
	@printf "$(OK_COLOR)==> Running pylinter$(NO_COLOR)\n"
	@pylint --recursive true main.py config pdf_report excel/

## deps: install dependencies
deps:
	@printf "$(OK_COLOR)==> Installing dependencies$(NO_COLOR)\n"
	. $(ENV_DIR)/bin/activate && pip install -r requirements.txt

## help: prints this help message
help:
	@echo "Usage:"
	@sed -n 's/^##//p' ${MAKEFILE_LIST} | column -t -s ':' |  sed -e 's/^/ /'

## generate: generate excel report
generate:
	@printf "$(OK_COLOR)==> Generating excel report$(NO_COLOR)\n"
	@python main.py

## env: create virtual env
env:
	@python3 -m venv $(ENV_DIR)

## setup: setup virtual env and requirements
setup: env deps
	@printf "$(OK_COLOR)==> Setting up project$(NO_COLOR)\n"
