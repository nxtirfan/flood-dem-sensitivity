#!/bin/sh
set -eu
# Isolated tools only; does not authenticate or execute any GEE graph.
python3 -m venv /tmp/t17-venv
/tmp/t17-venv/bin/pip install 'playwright==1.65.0' 'earthengine-api==1.7.52'
/tmp/t17-venv/bin/playwright install chromium
