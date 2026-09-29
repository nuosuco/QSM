#!/bin/bash
# verify_accuracy.sh <weight_src> <data_file> [classes] [pixels] [min] [max] [verbose]
# 示例: ./verify_accuracy.sh qdfs/ns/models qdfs/ns/data/yi_glyph_4226_32x32.data
#       ./verify_accuracy.sh models data.data 515 1024 0 20 1
cd "$(dirname "$0")"
A_SRC="$1" A_DATA="$2" A_NCLASS="${3:-515}" A_PIXELS="${4:-1024}" A_MIN="${5:-0}" A_MAX="${6:-0}" A_VERBOSE="${7:-0}" awk -f verify_accuracy.awk </dev/null
