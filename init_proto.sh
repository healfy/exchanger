#!/usr/bin/env bash
BONUM_BRANCH=$1

if [ ! -z "$BONUM_BRANCH" ] || [ "$BONUM_BRANCH" == dev ] || [ "$BONUM_BRANCH" == stage ] || [ "$BONUM_BRANCH" == prod ] || [ "$BONUM_BRANCH" == local ]; then
  if [ "$BONUM_BRANCH" == dev ]; then
    BRANCHES_PULL=dev
  elif [ "$BONUM_BRANCH" == stage ]; then
    BRANCHES_PULL=stage
  elif [ "$BONUM_BRANCH" == prod ]; then
    BRANCHES_PULL=master
  elif [ "$BONUM_BRANCH" == local ]; then
    BRANCHES_PULL=''
  fi
else
  BRANCHES_PULL=master
fi

cd `dirname $0`
git clone git@gitlab.com:bonum/proto.git
cd proto
git checkout $BRANCHES_PULL
git pull
