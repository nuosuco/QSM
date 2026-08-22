#!/bin/bash
set -e
cd "$(dirname "$0")/.."
SEQ=$(python3 build/qbootstrap.py --quiet --steps 10 --seeds "3,13" 2>/dev/null | grep SEQ | sed 's/SEQ=//')
python3 -c "
import os
os.chdir('/root/QSM/QLife')
cph2cls={}
for l in open('qdfs/ns/corpus/vocab_map.txt'):
    p=l.strip().split()
    if len(p)>=2: cph2cls[p[1]]=int(p[0])
cls2cph={v:k for k,v in cph2cls.items()}
cp2char={}
for l in open('qdfs/ns/data/yi_data_simple.data'):
    p=l.strip().split(chr(9))
    if len(p)>=2: cp2char[p[0]]=p[1]
seq=[$SEQ]
for cls in seq:
    cph=cls2cph.get(cls,'?')
    # cph='F2710' -> hex int 0xF2710
    try:
        cp=int(cph,16) if cph!='?' else -1
        ch=cp2char.get(str(cp),cph)
    except: ch=cph
    print(f'{cls} {cph} {ch}',end=' ')
print()
"
