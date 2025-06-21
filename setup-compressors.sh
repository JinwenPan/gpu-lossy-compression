#!/bin/bash

RED='\033[0;31m'
BOLDRED='\033[1;31m' 
GRAY='\033[0;37m'
NOCOLOR='\033[0m'

# cuszhi
echo "\n${BOLDRED}setting up cuszhi...${GRAY}"
cmake -S cuszhi -B cuszhi/build \
    -D PSZ_BACKEND=cuda \
    -D PSZ_BUILD_EXAMPLES=off \
    -D CMAKE_CUDA_ARCHITECTURES="80;86;89" \
    -D CMAKE_BUILD_TYPE=Release 
cmake --build cuszhi/build -- -j

echo -e "${NOCOLOR}"