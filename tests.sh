#!/bin/bash

coverage run --source clans tests/test_client.py
coverage html
