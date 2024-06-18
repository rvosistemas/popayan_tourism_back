# Makefile para ejecutar tests y ver cobertura

#TEST_COMMAND = pytest
#COVERAGE_COMMAND = coverage
#
## Objetivos
#.PHONY: test coverage clean
#
## Objetivo predeterminado (ejecutar tests y ver cobertura)
#all: test coverage
#
## Ejecutar todos los tests
#test:
#	@echo "Executing..."
#	export DJANGO_SETTINGS_MODULE=project.settings; \
#	$(TEST_COMMAND) -v tests/
#
## Generar informe de cobertura
#coverage:
#	@echo "Executing..."
#	export DJANGO_SETTINGS_MODULE=project.settings; \
#	$(COVERAGE_COMMAND) run -m $(TEST_COMMAND) tests/
#	$(COVERAGE_COMMAND) report -m --skip-covered
#
## Limpieza (eliminar archivos generados por coverage)
#clean:
#	$(COVERAGE_COMMAND) erase


MODULE = user_profile

c:
	@echo "Executing..."
	export DJANGO_SETTINGS_MODULE=project.settings;\
	pytest --cov=$(MODULE)/ \
	tests/$(MODULE)/ --cov-report term-missing -x -s -W \
	ignore::DeprecationWarning -o cache_dir=/tmp/application/cache

a:
	@echo "Executing..."
	export DJANGO_SETTINGS_MODULE=project.settings;\
	pytest --cov=./ \
	tests/ --cov-report term-missing -x -s -W \
	ignore::DeprecationWarning