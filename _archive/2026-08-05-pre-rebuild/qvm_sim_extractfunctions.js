    extractFunctions() {
        let i = 0;
        while(i < this.code.length) {
            if(this.code[i] === 0x66) {
                const sidx = this.code[i+1] | (this.code[i+2] << 8);
                const flen = this.code[i+3] | (this.code[i+4] << 8);
                const paramCount = this.code[i+5] | (this.code[i+6] << 8);
                i += 7;
                if(this.code[i] === 0xFF) i++;
                const funcName = this.readStrFromPool(sidx);
                this.funcs[funcName] = { start: i, params: [] };
                if(funcName==='main') console.log("[extract] main func found at start="+i+" params="+JSON.stringify(this.funcs[funcName].params));
                if(funcName!=='main' && funcName!=='') console.log("[extract] func '"+funcName+"' at pos="+i+" start="+this.funcs[funcName].start+" params="+JSON.stringify(this.funcs[funcName].params));
                for(let p = 0; p < paramCount; p++) {
                    if(i + 1 < this.code.length) {
                        const pidx = this.code[i] | (this.code[i+1] << 8);
                        this.funcs[funcName].params.push(pidx);
                        i += 2;
                    }
                }
                this.funcs[funcName].start = i;
                let depth = 1;
                while(i < this.code.length && depth > 0) {
                    const op = this.code[i];
                    if(op === 0xFE) { depth--; i++; }
                    else if(op === 0x66 && depth > 1) {
                        const noff = this.code[i+1] | (this.code[i+2] << 8);
                        const nflen = this.code[i+3] | (this.code[i+4] << 8);
                        if(noff + nflen <= this.spData.length) {
                            i += 7;
                            const npc = this.code[i-2] | (this.code[i-1] << 8);
                            if(this.code[i] === 0xFF) i++;
                            for(let p = 0; p < npc; p++) { i += 2; }
                            depth++;
                        } else { i++; }
                    }
                    else if(op === 0x67) { i++; if(depth <= 0) break; }
                    else if(op === 0x6c) { const cl = this.code[i+1] | (this.code[i+2] << 8); i += 3 + cl; }
                    else if(op === 0x6e) { const cl = this.code[i+1] | (this.code[i+2] << 8); i += 3 + cl; }
                    else if(op === 0x6d) { i++; }
                    else if(op === 0x0a) { i += 3; }
                    else if(op === 0x21 || op === 0x22 || op === 0x6a || op === 0x79) { i += 3; }
                    else if(op === 0x70) { i += 4; }
                    else if(op === 0x78) { i += 3; }
                    else if(op === 0x6b || op === 0xFF) { i++; }
                    else { i++; }
                }
                if(this.code[i] === 0x67) i++;
            } else {
                const op = this.code[i];
                i++;
                if(op === 0x0a) { i += 2; }
                else if(op === 0x21 || op === 0x22 || op === 0x6a || op === 0x79) { i += 2; }
                else if(op === 0x70) { i += 3; }
                else if(op === 0x78) { i += 2; }
                else if(op === 0x6c) { const cl = this.code[i] | (this.code[i+1] << 8); i += 2 + cl; }
                else if(op === 0x6e) { const cl = this.code[i] | (this.code[i+1] << 8); i += 2 + cl; }
                else if(op === 0x6d || op === 0x6f || op === 0xfe || op === 0x6b || op === 0xFF) { /* 1 byte */ }
                else { /* 1 byte */ }
            }
        }
        console.log("[extract] extractFunctions done");
    }

    readStrFromPool(idx) {
        let count = 0, pos = 0;
        while(pos < this.spData.length && count < idx) {
            while(pos < this.spData.length && this.spData[pos] !== 0) pos++;
            pos++;
            count++;
        }
        let s = '';
        while(pos < this.spData.length && this.spData[pos] !== 0) {
            s += String.fromCharCode(this.spData[pos]);
            pos++;
        }
        return s;
    }
