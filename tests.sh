#!/bin/bash

coverage run --source clans tests/test_scraper.py
coverage html
