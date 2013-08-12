#!/bin/bash

coverage run --source clans tests/test_scraper.py
coverage run --source clans --append tests/test_fmt.py
coverage run --source clans --append tests/test_ui.py
coverage html
