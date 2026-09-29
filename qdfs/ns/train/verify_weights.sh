#!/bin/bash
# verify_weights.sh <src> [classes] [pixels] [total]
# 示例: ./verify_weights.sh qdfs/ns/models
#       ./verify_weights.sh qdfs/ns/models 515 1024 527360
cd "$(dirname "$0")"
W_SRC="$1" W_CLASSES="${2:-515}" W_PIXELS="${3:-1024}" W_TOTAL="${4:-0}" awk -f verify_weights.awk </dev/null
