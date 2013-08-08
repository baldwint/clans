#!/bin/bash

coverage run --source clans tests/test_scraper.py
coverage run --source clans tests/test_fmt.py
coverage html
