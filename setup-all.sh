#!/bin/bash

RED='\033[0;31m'
BOLDRED='\033[1;31m' 
GRAY='\033[0;37m'
NOCOLOR='\033[0m'

export WORKSPACE=$(pwd)

export PATH=$(pwd)/cuszhi/build:$PATH

export PATH=$(pwd)/analyzer/build/examples:$PATH
export LD_LIBRARY_PATH=$(pwd)/analyzer/build/qcat:$LD_LIBRARY_PATH

if [ $# -eq 0 ]; then
    echo "bash setup-all.sh [arg1] [arg2]"
    echo "arg1:"
    echo "  * \"purge\"  to reset this workspace"
    echo "  * \"11\"     to initialize the project for CUDA 11"
    echo "  * \"12\"     to initialize the project for CUDA 12"
    echo "arg2:"
    echo "  * \"where to put data dirs\""
elif [ $# -eq 1 ]; then
    if [[ "$1" = "purge" ]]; then
        echo "purging build files..."
        rm -fr \
            cuszhi/build
    fi
elif [ $# -eq 2 ]; then 
    echo -e "\n${BOLDRED}specified CUDA version $1${NOCOLOR}"
    bash setup-compressors.sh
    bash setup-analyzer.sh

    export DATAPATH=$(readlink -f $2)
    echo -e "\n${BOLDRED}specified data path as "$2" (abs path: "${DATAPATH}")${NOCOLOR}"
fi
