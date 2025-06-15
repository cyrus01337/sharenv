#!/usr/bin/env bash
set -e

python -m build
pip install -U .
