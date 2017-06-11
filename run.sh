#!/bin/bash

set -e

if [ -d "fxc" ]; then
  SSSHARE_ARGS="--fxc-enabled"
  if [[ -z `ps u |grep "java -jar fxc/bin/fxc-webapi.jar" | grep -v grep` ]]; then
    echo "* Spawning FXC backend"
    java -jar fxc/bin/fxc-webapi.jar &
    FXC_PROC=`ps -ef | grep "java -jar fxc/bin/fxc-webapi.jar" | grep -v grep | awk '{print $2}'`
  else
    echo "* FXC backend already running"
  fi
fi

. venv/bin/activate
./run-ssshare $SSSHARE_ARGS


if [[ "" != $FXC_PROC ]]; then
  echo "*** Killing FXC backend"
  kill -9 $FXC_PROC
fi
