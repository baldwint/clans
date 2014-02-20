#!/bin/bash

# the $@ passes flags through
py.test --cov clans --cov-report html $@
