#!/bin/sh -e


export PREFIX=""
if [ -d 'venv' ] ; then
    export PREFIX="venv/bin/"
fi

set -x

pip install -r requirements/requirements-lint.txt

${PREFIX}autoflake --in-place --recursive --remove-all-unused-imports --remove-unused-variables src tests
${PREFIX}black --exclude=".pyi$" src tests
${PREFIX}isort --multi-line=3 --trailing-comma --force-grid-wrap=0 --combine-as --line-width 88 --recursive --apply src tests
