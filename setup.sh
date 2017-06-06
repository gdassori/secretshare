#!/bin/bash

set -e

if [ -z $(which python3.4) ]
 then
  echo """ERROR: Python 3.4 is required"""
  exit
fi
if [ -z $(which virtualenv) ]
 then
  echo """ERROR: Virtualenv is required"""
  exit
fi

rm -rf venv
virtualenv -p python3.4 venv
. venv/bin/activate
pip install -r requirements.txt
