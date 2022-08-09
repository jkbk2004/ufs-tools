#!/bin/bash

set -ex

usage() {
  set +x
  echo
  echo "Usage: $0 -f <branch> | -u <gitrepo> | -e <expdir> "
  echo
  echo "  -f  feature branch name to clone"
  echo "  -u  git repository url"
  echo "  -e  rt setup directory"
  echo
  set -x
  exit 1
}

[[ $# -eq 0 ]] && usage

while getopts f:u:e: flag

do
        case "${flag}" in
                f) BR=${OPTARG}
                        ;;
                u) FORK=${OPTARG}
                        ;;
                e) REPO=${OPTARG}
                        ;;
                *) echo "Invalid options: -$flag";
		        ;;
        esac

done

echo "feature branch to clone: $BR";
echo "forked branch URL: $FORK";
echo "experiment name: $REPO";
echo "current path" $(pwd);

CUR_PWD=$(pwd);

git clone -b $BR $FORK $REPO
cd $REPO
./manage_externals/checkout_externals
mkdir build
source env/build_orion_intel.env
cd build
cmake .. -DCMAKE_INSTALL_PREFIX=..
make -j 8 >& build.out &
cd $CUR_PWD
