#!/usr/bin/env node
const fs = require('fs');
const inputPath = process.argv[2];
let cycleCount = 0;

// ==================== 内置函数 ====================
const builtins = {};
function regBuiltin(name, fn) { builtins[name] = fn; }

regBuiltin('printf', function(args) {
    const fmt = String(args[0] || '');
    const vals = args.slice(1);
    let out = '', i = 0, vi = 0;
    while(i < fmt.length) {
        if(fmt[i] === '%' && i + 1 < fmt.length) {
            const c = fmt[i + 1];
            if(c === 's') { out += String(vals[vi++] || ''); i += 2; }
            else if(c === 'd') { out += String(~~vals[vi++]); i += 2; }
            else if(c === 'n') { out += '\n'; i += 2; }
            else { out += fmt[i]; i++; }
        } else { out += fmt[i]; i++; }
    }
    console.log(out);
});
regBuiltin('len', function(args) {
    return String(args[0] || '').length;
});
regBuiltin('error', function(args) {
    console.log('[ERROR] ' + (args[0] || ''));
    return 0;
});
regBuiltin('str_len', function(args) { return String(args[0] || '').length; });
regBuiltin('str_sub', function(args) { const s = String(args[0] || ''); const start = ~~args[1]; const len = ~~args[2]; return s.substring(start, start + len); });
regBuiltin('str_cat', function(args) { return args.map(a => String(a || '')).join(''); });
regBuiltin('str_cmp', function(args) { const a = String(args[0] || ''); const b = String(args[1] || ''); return a < b ? -1 : (a > b ? 1 : 0); });
regBuiltin('str_idx', function(args) { const s = String(args[0] || ''); const idx = ~~args[1]; return idx >= 0 && idx < s.length ? s.charCodeAt(idx) : 0; });
regBuiltin('file_read', function(args) { try { return fs.readFileSync(String(args[0] || ''), 'utf8'); } catch(e) { return ''; } });
regBuiltin('file_write', function(args) { try { fs.writeFileSync(String(args[0] || ''), String(args[1] || '')); } catch(e) {} });
regBuiltin('debug', function(args) { console.log('[DEBUG]', ...args); });

// ==================== QVM ====================
class QVM {
    constructor(code, spData) {
        this.code = code;
        this.spData = spData;
        this.pc = 0;
        this.stack = [];
        this.vars = {};
        this.cycles = 0;
        this.running = true;
        this.callStack = [];
        this.funcs = {};
        this.whilePc = 0;
        this.extractFunctions();
    }

    readStrIdx() {
        if(this.pc + 1 >= this.code.length) return '';
        const idx = this.code[this.pc] | (this.code[this.pc + 1] << 8);
        this.pc += 2;
        let count = 0, pos = 0;
        while(pos < this.spData.length && count < idx) {
            while(pos < this.spData.length && this.spData[pos] !== 0) pos++;
            pos++;
            count++;
        }
        if(pos >= this.spData.length) return '';
        let s = '';
        while(pos < this.spData.length && this.spData[pos] !== 0) {
            s += String.fromCharCode(this.spData[pos]);
            pos++;
        }
        return s;
    }

    getVar(name) { return this.vars[name] !== undefined ? this.vars[name] : 0; }

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
                if(funcName==='main') {
                    console.log("[extract] main func found at start="+i+" params="+JSON.stringify(this.funcs[funcName].params));
                }
                if(funcName!=='main' && funcName!=='') console.log("[extract] func '"+funcName+"' at pos="+i+" start="+this.funcs[funcName].start+" params="+JSON.stringify(this.funcs[funcName].params));
                // Skip function body: scan to matching BC_FUNC_END
                let depth = 1;
                while(i < this.code.length && depth > 0) {
                    const op = this.code[i];
                    if(op === 0xFE) { depth--; i++; }
                    else if(op === 0x66) {
                        // Another function definition inside this one
                        // Extract it and skip its body
                        const nidx = this.code[i+1] | (this.code[i+2] << 8);
                        const nname = this.readStrFromPool(nidx);
                        if(!this.funcs[nname]) {
                            this.funcs[nname] = { start: i+7+1, params: [] };
                            if(nname!=='main' && nname!=='') console.log("[extract] func '"+nname+"' at pos="+(i+7+1));
                        }
                        i += 7;
                        if(this.code[i] === 0xFF) i++;
                        depth++;
                    }
                    else if(op === 0x67) { i++; if(depth <= 0) break; }
                    else if(op === 0x6c) { const cl = this.code[i+1] | (this.code[i+2] << 8); i += 3 + cl; }
                    else if(op === 0x6e) { const cl = this.code[i+1] | (this.code[i+2] << 8); i += 3 + cl; }
                    else if(op === 0x6d) { i++; }
                    else if(op === 0x0a) { i += 3; }
                    else if(op === 0x21 || op === 0x22 || op === 0x6a || op === 0x79) { i += 3; }
                    else if(op === 0x70) { i += 4; }
                    else if(op === 0x78) { i += 3; }
                    else if(op === 0x6b || op === 0xFF || op === 0x0E) { i++; }
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

    skipToElseOrEnd() {
        let depth = 1;
        while(this.pc < this.code.length && depth > 0) {
            const op = this.code[this.pc];
            if(op === 0x6f) { depth--; this.pc++; }
            else if(op === 0x6c || op === 0x6e) { depth++; this.pc++; }
            else if(op === 0x6d) { this.pc++; if(depth === 1) { depth = 0; break; } }
            else if(op === 0x6c) { const cl = this.code[this.pc] | (this.code[this.pc+1] << 8); this.pc += 3 + cl; }
            else if(op === 0x6e) { const cl = this.code[this.pc] | (this.code[this.pc+1] << 8); this.pc += 3 + cl; }
            else if(op === 0x66) { this.pc += 7; }
            else if(op === 0x0a) { this.pc += 3; }
            else if(op === 0x21 || op === 0x22 || op === 0x6a || op === 0x79) { this.pc += 3; }
            else if(op === 0x70) { this.pc += 4; }
            else if(op === 0x78) { this.pc += 3; }
            else if(op === 0x6b || op === 0xFF) { this.pc++; }
            else { this.pc++; }
        }
    }

    run() {
        const maxCycles = 100000;
        this.cycles = 0;
        this.running = true;

        if(this.funcs['main']) {
            this.pc = this.funcs['main'].start;
        }

        while(this.running && this.pc < this.code.length && this.cycles < maxCycles) {
            this.cycles++;
            cycleCount = this.cycles;
            const op = this.code[this.pc];
            this.pc++;
            if(op===0x70) console.log("[cycle "+this.cycles+"] pc="+(this.pc-1)+" op=0x70 fname="+this.readStrIdxFast(this.code[this.pc]|(this.code[this.pc+1]<<8)));

            switch(op) {
                case 0x00: break;

                case 0x78: {
                    this.stack.push(this.code[this.pc] | (this.code[this.pc+1] << 8));
                    this.pc += 2;
                    break;
                }
                case 0x79: {
                    this.stack.push(this.readStrIdx() || '');
                    break;
                }
                case 0x22: case 34: {
                    const name = this.readStrIdx();
                    this.stack.push(this.getVar(name));
                    break;
                }
                case 0x21: {
                    const name = this.readStrIdx();
                    this.vars[name] = this.stack.length > 0 ? this.stack.pop() : 0;
                    break;
                }
                case 0x6a: {
                    const name = this.readStrIdx();
                    this.vars[name] = this.stack.length > 0 ? this.stack.pop() : 0;
                    break;
                }
                case 0x6f: break;
                case 0x6b: {
                    if(this.callStack.length > 0) {
                        const ret = this.callStack.pop();
                        this.pc = ret.pc;
                        this.vars = ret.vars;
                    } else {
                        // main function return: stop execution
                        this.running = false;
                    }
                    break;
                }
                case 0xFE: {
                    // BC_FUNC_END: pop call stack and return to caller
                    if(this.callStack.length > 0) {
                        const ret = this.callStack.pop();
                        this.pc = ret.pc;
                        this.vars = ret.vars;
                    } else {
                        // main function end: stop execution
                        this.running = false;
                    }
                    break;
                }
                case 0x67: break;

                case 0x10: {
                    const b = this.stack.pop(); const a = this.stack.pop();
                    this.stack.push(a + b);
                    break;
                }
                case 0x0d: {
                    const b = this.stack.pop(); const a = this.stack.pop();
                    this.stack.push(a - b);
                    break;
                }
                case 0x0f: {
                    const b = this.stack.pop(); const a = this.stack.pop();
                    this.stack.push(a * b);
                    break;
                }
                case 0x0e: {
                    const b = this.stack.pop(); const a = this.stack.pop();
                    this.stack.push(b !== 0 ? Math.floor(a / b) : 0);
                    break;
                }
                case 0x0b: {
                    const v = this.stack.length > 0 ? this.stack.pop() : 0;
                    process.stdout.write(String(v));
                    break;
                }
                case 0x0c: {
                    this.running = false;
                    break;
                }
                case 0x0a: {
                    const target = this.code[this.pc] | (this.code[this.pc+1] << 8);
                    this.pc = target;
                    break;
                }
                case 0x1e: {
                    const a = this.stack.pop();
                    this.stack.push(a ? 0 : 1);
                    break;
                }
                case 0x20: {
                    const b = this.stack.pop(); const a = this.stack.pop();
                    this.stack.push(a && b ? 1 : 0);
                    break;
                }
                case 0x1F: {
                    const b = this.stack.pop(); const a = this.stack.pop();
                    this.stack.push(a || b ? 1 : 0);
                    break;
                }
                case 0xa3: {
                    const b = this.stack.pop(); const a = this.stack.pop();
                    this.stack.push(a === b ? 1 : 0);
                    break;
                }
                case 0xa4: {
                    const b = this.stack.pop(); const a = this.stack.pop();
                    this.stack.push(a !== b ? 1 : 0);
                    break;
                }
                case 0xa5: {
                    const b = this.stack.pop(); const a = this.stack.pop();
                    this.stack.push(a < b ? 1 : 0);
                    break;
                }
                case 0xa6: {
                    const b = this.stack.pop(); const a = this.stack.pop();
                    this.stack.push(a > b ? 1 : 0);
                    break;
                }
                case 0xa7: {
                    const b = this.stack.pop(); const a = this.stack.pop();
                    this.stack.push(a <= b ? 1 : 0);
                    break;
                }
                case 0xa8: {
                    const b = this.stack.pop(); const a = this.stack.pop();
                    this.stack.push(a >= b ? 1 : 0);
                    break;
                }
                case 0x6c: case 108: {
                    const codeLen = this.code[this.pc] | (this.code[this.pc+1] << 8);
                    const condStart = this.pc + 2;
                    this.pc += 2 + codeLen;
                    const savedPc = this.pc;
                    this.pc = condStart;
                    while(this.pc < condStart + codeLen) {
                        this.cycles++;
                        cycleCount = this.cycles;
                        const subOp = this.code[this.pc];
                        this.pc++;
                        switch(subOp) {
                            case 0x00: break;
                            case 0x78: { this.stack.push(this.code[this.pc] | (this.code[this.pc+1] << 8)); this.pc += 2; break; }
                            case 0x79: this.stack.push(this.readStrIdx() || ''); break;
                            case 0x22: { const n = this.readStrIdx(); this.stack.push(this.getVar(n)); break; }
                            case 0x21: this.readStrIdx(); if(this.stack.length > 0) this.stack.pop(); break;
                            case 0x6a: this.vars[this.readStrIdx()] = this.stack.length > 0 ? this.stack.pop() : 0; break;
                            case 0x6f: break;
                            case 0x6b: break;
                            case 0x70: { const fn = this.readStrIdx(); const nargs = this.code[this.pc++]; const a = []; for(let i=0;i<nargs&&this.stack.length>0;i++) a.unshift(this.stack.pop()); if(builtins[fn]) { const r = builtins[fn](a, this); if(r !== undefined) this.stack.push(r); } break; }
                            case 0x0d: { const b = this.stack.pop(); const a = this.stack.pop(); this.stack.push(a - b); break; }
                            case 0x0e: { const b = this.stack.pop(); const a = this.stack.pop(); this.stack.push(b !== 0 ? Math.floor(a / b) : 0); break; }
                            case 0x0f: { const b = this.stack.pop(); const a = this.stack.pop(); this.stack.push(a * b); break; }
                            case 0x10: { const b = this.stack.pop(); const a = this.stack.pop(); this.stack.push(a + b); break; }
                            case 0xa3: { const b = this.stack.pop(); const a = this.stack.pop(); this.stack.push(a === b ? 1 : 0); break; }
                            case 0xa4: { const b = this.stack.pop(); const a = this.stack.pop(); this.stack.push(a !== b ? 1 : 0); break; }
                            case 0xa5: { const b = this.stack.pop(); const a = this.stack.pop(); this.stack.push(a < b ? 1 : 0); break; }
                            case 0xa6: { const b = this.stack.pop(); const a = this.stack.pop(); this.stack.push(a > b ? 1 : 0); break; }
                            case 0xa7: { const b = this.stack.pop(); const a = this.stack.pop(); this.stack.push(a <= b ? 1 : 0); break; }
                            case 0xa8: { const b = this.stack.pop(); const a = this.stack.pop(); this.stack.push(a >= b ? 1 : 0); break; }
                            case 0x20: { const b = this.stack.pop(); const a = this.stack.pop(); this.stack.push(a && b ? 1 : 0); break; }
                            case 0x1e: { const a = this.stack.pop(); this.stack.push(a ? 0 : 1); break; }
                            default: this.pc++;
                        }
                    }
                    this.pc = savedPc;
                    const cond = this.stack.length > 0 ? this.stack.pop() : 0;
                    if(!cond) { this.skipToElseOrEnd(); }
                    break;
                }
                case 0x0a: case 10: // JUMP (loop back)
                    pc = this.code[pc+1] | (this.code[pc+2] << 8);
                    break;
                case 0x6d: case 109:
                    this.skipToElseOrEnd(); break;
                case 0x6e: {
                    const condStart = this.pc + 2;
                    const codeLen = this.code[this.pc] | (this.code[this.pc+1] << 8);
                    const bodyStart = this.pc + 2 + codeLen;
                    const whilePc = this.pc - 1;
                    this.pc = condStart;
                    while(this.pc < condStart + codeLen) {
                        this.cycles++;
                        cycleCount = this.cycles;
                        const subOp = this.code[this.pc];
                        this.pc++;
                        switch(subOp) {
                            case 0x00: break;
                            case 0x78: { this.stack.push(this.code[this.pc] | (this.code[this.pc+1] << 8)); this.pc += 2; break; }
                            case 0x79: this.stack.push(this.readStrIdx() || ''); break;
                            case 0x22: { const n = this.readStrIdx(); this.stack.push(this.getVar(n)); break; }
                            case 0x21: this.readStrIdx(); if(this.stack.length > 0) this.stack.pop(); break;
                            case 0x6a: this.vars[this.readStrIdx()] = this.stack.length > 0 ? this.stack.pop() : 0; break;
                            case 0x6f: break;
                            case 0x6b: break;
                            case 0x70: { const fn = this.readStrIdx(); const nargs = this.code[this.pc++]; const a = []; for(let i=0;i<nargs&&this.stack.length>0;i++) a.unshift(this.stack.pop()); if(builtins[fn]) { const r = builtins[fn](a, this); if(r !== undefined) this.stack.push(r); } break; }
                            case 0x0d: { const b = this.stack.pop(); const a = this.stack.pop(); this.stack.push(a - b); break; }
                            case 0x0e: { const b = this.stack.pop(); const a = this.stack.pop(); this.stack.push(b !== 0 ? Math.floor(a / b) : 0); break; }
                            case 0x0f: { const b = this.stack.pop(); const a = this.stack.pop(); this.stack.push(a * b); break; }
                            case 0x10: { const b = this.stack.pop(); const a = this.stack.pop(); this.stack.push(a + b); break; }
                            case 0xa3: { const b = this.stack.pop(); const a = this.stack.pop(); this.stack.push(a === b ? 1 : 0); break; }
                            case 0xa4: { const b = this.stack.pop(); const a = this.stack.pop(); this.stack.push(a !== b ? 1 : 0); break; }
                            case 0xa5: { const b = this.stack.pop(); const a = this.stack.pop(); this.stack.push(a < b ? 1 : 0); break; }
                            case 0xa6: { const b = this.stack.pop(); const a = this.stack.pop(); this.stack.push(a > b ? 1 : 0); break; }
                            case 0xa7: { const b = this.stack.pop(); const a = this.stack.pop(); this.stack.push(a <= b ? 1 : 0); break; }
                            case 0xa8: { const b = this.stack.pop(); const a = this.stack.pop(); this.stack.push(a >= b ? 1 : 0); break; }
                            case 0x20: { const b = this.stack.pop(); const a = this.stack.pop(); this.stack.push(a && b ? 1 : 0); break; }
                            case 0x1e: { const a = this.stack.pop(); this.stack.push(a ? 0 : 1); break; }
                            default: this.pc++;
                        }
                    }
                    const cond = this.stack.length > 0 ? this.stack.pop() : 0;
                    if(!cond) {
                        this.pc = bodyStart;
                        this.skipToElseOrEnd();
                    } else {
                        this.pc = bodyStart;
                    }
                    this.whilePc = whilePc;
                    break;
                }
                case 0x70: case 112: {
                    const fname = this.readStrIdx();
                    if(fname==='printf') console.log('[NATIVE_CALL] printf fname="'+fname+'" builtins[printf]='+!!builtins[fname]+' funcs[printf]='+!!this.funcs[fname]);
                    if(!this.funcs[fname] && !builtins[fname]) {
                        this.pc++;
                        if(fname!=='') console.log('[NATIVE_CALL] SKIP: unknown function "'+fname+'"');
                        break;
                    }
                    const nargs = this.code[this.pc]; this.pc++;
                    const args = [];
                    for(let i = 0; i < nargs; i++) args.unshift(this.stack.length > 0 ? this.stack.pop() : 0);
                    if(builtins[fname]) {
                        if(fname==='printf') console.log('[NATIVE_CALL] printf called with args:', args.map(a=>typeof a==='string'?'"'+a+'"':a).join(','));
                        const result = builtins[fname](args, this);
                        if(result !== undefined) this.stack.push(result);
                    } else if(this.funcs[fname]) {
                        // 设置参数
                        const func = this.funcs[fname];
                        for(let p = 0; p < func.params.length && p < args.length; p++) {
                            const pname = this.readStrIdxFast(func.params[p]);
                            this.vars[pname] = args[p];
                        }
                        this.callStack.push({pc: this.pc, vars: {...this.vars}});
                        this.pc = func.start;
                    }
                    break;
                }
                case 0x66: { 
                    // FUNC_DEF: skip entire function (header + body)
                    // No param indices in bytecode - just skip 0xFF and body
                    // Note: this.pc already incremented past opcode, so sidx at this.pc+0
                    let skip = 6;  // sidx(2)+flen(2)+paramCount(2) = 6 bytes from this.pc
                    if(this.code[this.pc+6] === 0xFF) skip++;
                    // Skip body: scan to matching BC_FUNC_END
                    let depth = 1;
                    let j = this.pc + skip;
                    while(j < this.code.length && depth > 0) {
                        const op = this.code[j];
                        if(op === 0xFE) { depth--; if(depth===0) { j++; break; } j++; }
                        else if(op === 0x66) { 
                            // j is at start of nested FUNC_DEF opcode
                            j += 7;  // skip 7-byte header (opcode+sidx+flen+paramCount)
                            if(this.code[j] === 0xFF) j++;
                            depth++;
                        }
                        else if(op === 0x67) { j++; if(depth <= 0) break; }
                        else if(op === 0x6c) { const cl = this.code[j+1] | (this.code[j+2] << 8); j += 3 + cl; }
                        else if(op === 0x6e) { const cl = this.code[j+1] | (this.code[j+2] << 8); j += 3 + cl; }
                        else if(op === 0x6d) { j++; }
                        else if(op === 0x0a) { j += 3; }
                        else if(op === 0x21 || op === 0x22 || op === 0x6a || op === 0x79) { j += 3; }
                        else if(op === 0x70) { j += 4; }
                        else if(op === 0x78) { j += 3; }
                        else if(op === 0x6b || op === 0xFF || op === 0x0E) { j++; }
                        else { j++; }
                    }
                    this.pc = j;
                    if(this.code[this.pc] === 0x67) this.pc++;
                    break;
                }
                default:
                    console.log('[QVM] 未知opcode: 0x' + op.toString(16) + ' (pos=' + (this.pc-1) + ')');
                    this.running = false;
                    break;
            }
        }
        console.log('[QVM] 执行完成: ' + this.cycles + ' 周期');
    }

    readStrIdxFast(idx) {
        let count = 0, pos = 0;
        while(pos < this.spData.length && count < idx) {
            while(pos < this.spData.length && this.spData[pos] !== 0) pos++;
            pos++;
            count++;
        }
        if(pos >= this.spData.length) return '';
        let s = '';
        while(pos < this.spData.length && this.spData[pos] !== 0) {
            s += String.fromCharCode(this.spData[pos]);
            pos++;
        }
        return s;
    }
}

if(!inputPath) {
    console.log('用法: node qvm_sim.js <input.qbc>');
    process.exit(1);
}

const data = fs.readFileSync(inputPath);
const magic = data[0];
if(magic !== 0x14) {
    console.log('[QVM] 无效的字节码格式');
    process.exit(1);
}
const codeLen = data.readUInt16LE(4);
const code = Array.from(data.slice(6, 6 + codeLen));
const spLen = data.readUInt16LE(6 + codeLen);
const spData = Array.from(data.slice(8 + codeLen, 8 + codeLen + spLen));

console.log('[QVM] 加载QEntL字节码: code_len=' + codeLen + ', sp_len=' + spLen);

const vm = new QVM(code, spData);
vm.run();