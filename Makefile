.PHONY: help
help:
	@echo "install            : Install the package (crea_scraper)"
	@echo "kernel-install     : Intall the poetry env as kernel for notebook development"
	@echo "git-init           : Initialize the project as git repo (to allow pre-commit use)"
	@echo "pre-commit-install : Install pre-commit hooks"
	@echo "pre-commit         : Run pre-commit on all files"
	@echo "setup-dev          : Run series of commands to setup dev environment"
	@echo "setup              : Run the make install command"

.PHONY: install
install:
	poetry install

.PHONY: kernel-install
kernel-install:
	poetry run ipython kernel install --user --name=crea-scraper

.PHONY: git-init
git-init:
	poetry run git init
	poetry run git add .
	poetry run git commit -m "Init"

.PHONY: pre-commit-install
pre-commit-install:
	poetry run pre-commit install

.PHONY: pre-commit
pre-commit:
	poetry run pre-commit run -a

.PHONY: setup-dev
setup-dev: install kernel-install git-init pre-commit-install

.PHONY: setup
setup: install
