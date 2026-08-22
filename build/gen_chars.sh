#!/bin/bash
set -e
cd "$(dirname "$0")/.."
if [ ! -f /tmp/qb_gen.qbc ]; then
    bin/qvm_boot compile build/qb_gen.qentl /tmp/qb_gen.qbc >/dev/null 2>&1
fi
SEQ=$(bin/qvm_boot run /tmp/qb_gen.qbc 2>/dev/null | grep SEQ | sed 's/SEQ=//')
echo "SEQ=$SEQ"
