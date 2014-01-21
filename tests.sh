#!/bin/bash

# the $@ passes flags through
py.test --capture sys --cov clans --cov-report html $@
