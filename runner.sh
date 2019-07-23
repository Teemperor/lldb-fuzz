#!/bin/bash

$lldb=$1

clang++ -g -std=c++11 main.cpp -o tt

$lldb ./hello_pp -o "command script import /Users/teemperor/fuzz.py" -o "fuzz 1"  -b
