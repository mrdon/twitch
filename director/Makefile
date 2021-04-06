.PHONY: run tunnel client help venv format run


# Help system from https://marmelab.com/blog/2016/02/29/auto-documented-makefile.html
.DEFAULT_GOAL := help

help:
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

venv: ## Create python venv
	python3.8 -m venv venv
	venv/bin/pip install pip-tools
	venv/bin/pip-compile
	venv/bin/pip install -r requirements.txt
	
format: ## Format the code
	venv/bin/black director
	venv/bin/reorder-python-imports --py38-plus `find director -name "*.py"` || venv/bin/black director --target-version py38


run: ## Run the app locally
	hypercorn director.web:app
