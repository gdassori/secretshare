#!/bin/bash

set -e

CURRENT_PATH=$(pwd)

if [ -z $(which python3.4) ]; then
  echo """ERROR: Python 3.4 is required"""
  exit
fi
if [ -z $(which virtualenv) ]; then
  echo """ERROR: Virtualenv is required"""
  exit
fi
rm -rf fxc

if [ "$1" == "--disable-fxc" ]; then
 echo "Skipping FXC Build"
elif [ -z "$1" ]; then
 echo """
Building FXC
"""
  if [ -z $(which java) ]; then
    echo """ERROR: Java is required"""
    exit
  fi
  if [ -z $(which git) ]; then
    echo """ERROR: git is required"""
    exit
  fi
  mkdir -p fxc/src ; mkdir fxc/bin
  if [ -z $(which lein) ]; then
    echo "Downloading Leingen"
    cd $CURRENT_PATH/fxc/bin
    curl https://raw.githubusercontent.com/technomancy/leiningen/stable/bin/lein > lein
    chmod a+x lein
  fi
  cd $CURRENT_PATH/fxc/src
  git clone https://github.com/dyne/FXC-webapi.git
  cd FXC-webapi
  $CURRENT_PATH/fxc/bin/lein do clean, ring uberjar
  mv target/server.jar $CURRENT_PATH/fxc/bin/fxc-webapi.jar
  echo "FXC-webapi built"
  cd $CURRENT_PATH

else
 echo """
Ssshare build script

Arguments:
  --disable-fxc Disable FXC Build [ native \ skip ]

  --help Show this help
"""
  exit
fi

rm -rf venv
virtualenv -p python3.4 venv
. venv/bin/activate
pip install -r requirements.txt
chmod +x run-ssshare

python -m unittest