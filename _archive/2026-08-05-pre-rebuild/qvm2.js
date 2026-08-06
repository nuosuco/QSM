#!/usr/bin/env node
const fs=require('fs');

// Opcode values matching qcl.qentl constants
const OP = {
  PUSH_INT: 1, PUSH_STR: 2, LOAD_VAR: 3, STORE_VAR: 4,
  ADD: 5, SUB: 6, MUL: 7, DIV: 8, MOD: 9,
  EQ: 10, NEQ: 11, LT: 12, GT: 13, LE: 14, GE: 15,
  JMP: 16, JMP_FALSE: 17, CALL: 18, RET: 19, HALT: 20,
  BUILTIN: 21, ARRAY_NEW: 22, ARRAY_GET: 23, ARRAY_SET: 24,
  POP: 25, NEG: 26, NOT: 27, AND: 28, OR: 29,
  FUNC_DEF: 30, FUNC_END: 31
};

// Builtin functions by pool order (as they are added to pool in qcl.qentl)
// These are looked up by PID (pool index)
const BUILTINS = {};

function registerBuiltin(name, fn) {
  BUILTINS[name] = fn;
}

registerBuiltin("printf", function(args, vm) {
  if(args.length===0) return;
  let fmt = typeof args[0]==='string'?args[0]:String(args[0]);
  let argIdx=1, result='';
  for(let i=0;i<fmt.length;i++) {
    if(fmt[i]==='%'&&i+1<fmt.length) {
      const spec=fmt[i+1];
      if(spec==='s'||spec==='d'||spec==='n') {
        result += argIdx<args.length?args[argIdx]:'';
        argIdx++; i++; continue;
      }
    }
    result += fmt[i];
  }
  process.stdout.write(result);
});

registerBuiltin("str_len", function(a){return typeof a[0]==='string'?a[0].length:0;});
registerBuiltin("str_char_at", function(a){
  const s=a[0], p=a[1]||0;
  if(typeof s==='string'&&p>=0&&p<s.length) return s[p];
  return '';
});
registerBuiltin("str_substring", function(a){
  const s=a[0], st=a[1]||0, en=a[2]||s.length;
  if(typeof s==='string') return s.substring(st,en);
  return '';
});
registerBuiltin("str_concat", function(a){let r='';for(let i=0;i<a.length;i++)r+=a[i];return r;});
registerBuiltin("str_eq", function(a){return a[0]===a[1]?1:0;});
registerBuiltin("str_index_of", function(a){
  const s=a[0], sub=a[1];
  if(typeof s==='string'&&typeof sub==='string') return s.indexOf(sub);
  return -1;
});
registerBuiltin("str_from_char", function(a){return String.fromCharCode(a[0]||0);});
registerBuiltin("str_to_int", function(a){return parseInt(a[0])||0;});
registerBuiltin("int_to_str", function(a){return String(a[0]);});
registerBuiltin("len", function(a){
  if(typeof a[0]==='string') return a[0].length;
  if(typeof a[0]==='number') return String(a[0]).length;
  return 0;
});
registerBuiltin("file_read", function(a,vm){
  try{if(a.length>0)return fs.readFileSync(a[0],'utf8');}catch(e){}
  return '';
});
registerBuiltin("file_write_bytes", function(a,vm){
  if(a.length>1) fs.writeFileSync(a[0], Buffer.from(a[1],'utf8'));
  return 0;
});
registerBuiltin("file_exists", function(a,vm){return fs.existsSync(a[0])?1:0;});
registerBuiltin("exit", function(){process.exit(0);});

class QVM2 {
  constructor(code) {
    this.code = code;
    this.pc = 0;
    this.stack = [];
    this.vars = new Map(); // slot -> value
    this.callStack = [];
    this.running = true;
    this.cycles = 0;
    this.funcs = new Map(); // name -> {start, nparams}
    this.pool = []; // string pool
    this.poolMap = new Map(); // string -> pid
  }

  loadPool(poolData) {
    let pos = 0;
    while(pos < poolData.length) {
      let s = '';
      while(pos < poolData.length && poolData[pos] !== 0) {
        s += String.fromCharCode(poolData[pos]);
        pos++;
      }
      this.pool.push(s);
      this.poolMap.set(s, this.pool.length - 1);
      pos++; // skip null
    }
  }

  readU16() {
    const v = this.code[this.pc] | (this.code[this.pc+1] << 8);
    this.pc += 2;
    return v;
  }

  readU8() {
    return this.code[this.pc++];
  }

  getPoolStr(pid) {
    if(pid >= 0 && pid < this.pool.length) return this.pool[pid];
    return '';
  }

  findBuiltin(name) {
    const fn = BUILTINS[name];
    if(fn) return fn;
    return null;
  }

  extractFunctions() {
    let i = 0;
    while(i < this.code.length - 3) {
      if(this.code[i] === OP.FUNC_DEF) {
        const namePid = this.code[i+1] | (this.code[i+2] << 8);
        const nparams = this.code[i+3];
        const name = this.getPoolStr(namePid);
        if(name) {
          // Find end of function
          let depth = 1;
          let j = i + 4 + nparams * 2;
          while(j < this.code.length && depth > 0) {
            const op = this.code[j];
            if(op === OP.FUNC_DEF) depth++;
            if(op === OP.FUNC_END) depth--;
            j++;
          }
          this.funcs.set(name, {start: i + 4 + nparams * 2, nparams: nparams, end: j});
          console.log('[extract] func: '+name+' start='+(i+4+nparams*2)+' nparams='+nparams);
        }
        // Skip past function
        let depth = 1;
        let j = i + 4 + nparams * 2;
        while(j < this.code.length && depth > 0) {
          if(this.code[j] === OP.FUNC_DEF) depth++;
          if(this.code[j] === OP.FUNC_END) depth--;
          j++;
        }
        i = j;
      } else {
        i++;
      }
    }
    console.log('[extract] found '+this.funcs.size+' functions');
  }

  getVarSlot(slot) {
    // Check current scope first, then global
    for(let i = this.callStack.length; i >= 0; i--) {
      const scope = i < this.callStack.length ? this.callStack[i].vars : this.vars;
      // flat scope - use single vars map
    }
    return this.vars.has(slot) ? this.vars.get(slot) : 0;
  }

  run() {
    try {
      while(this.running && this.pc < this.code.length) {
        this.cycles++;
        const op = this.code[this.pc++];
        switch(op) {
          case OP.PUSH_INT: {
            const v = this.readU16();
            this.stack.push(v);
            break;
          }
          case OP.PUSH_STR: {
            const pid = this.readU16();
            this.stack.push(this.getPoolStr(pid));
            break;
          }
          case OP.LOAD_VAR: {
            const slot = this.readU16();
            this.stack.push(this.getVarSlot(slot));
            break;
          }
          case OP.STORE_VAR: {
            const slot = this.readU16();
            this.vars.set(slot, this.stack.length > 0 ? this.stack.pop() : 0);
            break;
          }
          case OP.ADD: {
            const b = this.stack.pop(); const a = this.stack.pop();
            this.stack.push(a + b);
            break;
          }
          case OP.SUB: {
            const b = this.stack.pop(); const a = this.stack.pop();
            this.stack.push(a - b);
            break;
          }
          case OP.MUL: {
            const b = this.stack.pop(); const a = this.stack.pop();
            this.stack.push(a * b);
            break;
          }
          case OP.DIV: {
            const b = this.stack.pop(); const a = this.stack.pop();
            this.stack.push(b !== 0 ? Math.floor(a / b) : 0);
            break;
          }
          case OP.MOD: {
            const b = this.stack.pop(); const a = this.stack.pop();
            this.stack.push(b !== 0 ? a % b : 0);
            break;
          }
          case OP.EQ: {
            const b = this.stack.pop(); const a = this.stack.pop();
            this.stack.push(a === b ? 1 : 0);
            break;
          }
          case OP.NEQ: {
            const b = this.stack.pop(); const a = this.stack.pop();
            this.stack.push(a !== b ? 1 : 0);
            break;
          }
          case OP.LT: {
            const b = this.stack.pop(); const a = this.stack.pop();
            this.stack.push(a < b ? 1 : 0);
            break;
          }
          case OP.GT: {
            const b = this.stack.pop(); const a = this.stack.pop();
            this.stack.push(a > b ? 1 : 0);
            break;
          }
          case OP.LE: {
            const b = this.stack.pop(); const a = this.stack.pop();
            this.stack.push(a <= b ? 1 : 0);
            break;
          }
          case OP.GE: {
            const b = this.stack.pop(); const a = this.stack.pop();
            this.stack.push(a >= b ? 1 : 0);
            break;
          }
          case OP.JMP: {
            const offset = this.readU16();
            this.pc = offset;
            break;
          }
          case OP.JMP_FALSE: {
            const offset = this.readU16();
            const cond = this.stack.length > 0 ? this.stack.pop() : 0;
            if(!cond) this.pc = offset;
            break;
          }
          case OP.CALL: {
            const pid = this.readU16();
            const nargs = this.readU8();
            const name = this.getPoolStr(pid);
            const args = [];
            for(let i = 0; i < nargs; i++) args.unshift(this.stack.length > 0 ? this.stack.pop() : 0);
            const func = this.funcs.get(name);
            if(func) {
              this.callStack.push({pc: this.pc, vars: new Map(this.vars)});
              // Set up params
              for(let i = 0; i < nargs && i < func.nparams; i++) {
                this.vars.set(i, args[i]);
              }
              this.pc = func.start;
            }
            break;
          }
          case OP.RET: {
            if(this.callStack.length > 0) {
              const ret = this.callStack.pop();
              this.vars = ret.vars;
              this.pc = ret.pc;
            } else {
              this.running = false;
            }
            break;
          }
          case OP.HALT: {
            this.running = false;
            break;
          }
          case OP.BUILTIN: {
            const pid = this.readU16();
            const nargs = this.readU8();
            const name = this.getPoolStr(pid);
            const args = [];
            for(let i = 0; i < nargs; i++) args.unshift(this.stack.length > 0 ? this.stack.pop() : 0);
            const fn = this.findBuiltin(name);
            if(fn) {
              const result = fn(args, this);
              if(result !== undefined) this.stack.push(result);
            }
            break;
          }
          case OP.ARRAY_NEW: {
            const size = this.readU16();
            const arr = new Array(size).fill(0);
            this.stack.push(arr);
            break;
          }
          case OP.ARRAY_GET: {
            const slot = this.readU16();
            const idx = this.stack.length > 0 ? this.stack.pop() : 0;
            const arr = this.vars.get(slot) || [];
            this.stack.push(typeof arr[idx] === 'number' ? arr[idx] : 0);
            break;
          }
          case OP.ARRAY_SET: {
            const slot = this.readU16();
            const val = this.stack.length > 0 ? this.stack.pop() : 0;
            const idx = this.stack.length > 0 ? this.stack.pop() : 0;
            let arr = this.vars.get(slot);
            if(!arr || !Array.isArray(arr)) {
              arr = new Array(65536).fill(0);
              this.vars.set(slot, arr);
            }
            arr[idx] = val;
            break;
          }
          case OP.POP: {
            if(this.stack.length > 0) this.stack.pop();
            break;
          }
          case OP.NEG: {
            const a = this.stack.length > 0 ? this.stack.pop() : 0;
            this.stack.push(-a);
            break;
          }
          case OP.NOT: {
            const a = this.stack.length > 0 ? this.stack.pop() : 0;
            this.stack.push(a ? 0 : 1);
            break;
          }
          case OP.AND: {
            const b = this.stack.pop(); const a = this.stack.pop();
            this.stack.push((a && b) ? 1 : 0);
            break;
          }
          case OP.OR: {
            const b = this.stack.pop(); const a = this.stack.pop();
            this.stack.push((a || b) ? 1 : 0);
            break;
          }
          case OP.FUNC_DEF: {
            // Skip function definition
            const namePid = this.readU16();
            const nparams = this.readU8();
            // Skip param names
            for(let i = 0; i < nparams; i++) this.readU16();
            // Skip until FUNC_END
            let depth = 1;
            while(this.pc < this.code.length && depth > 0) {
              if(this.code[this.pc] === OP.FUNC_DEF) depth++;
              if(this.code[this.pc] === OP.FUNC_END) depth--;
              this.pc++;
            }
            break;
          }
          case OP.FUNC_END: {
            // Should not be reached in normal execution
            if(this.callStack.length > 0) {
              const ret = this.callStack.pop();
              this.vars = ret.vars;
              this.pc = ret.pc;
            } else {
              this.running = false;
            }
            break;
          }
          default:
            console.log('[QVM] 未知opcode: '+op+' (pc='+(this.pc-1)+')');
            this.running = false;
            break;
        }
      }
    } catch(e) {
      console.log('QVM error: '+e.message+'\n'+e.stack);
    }
    console.log('cycles: '+this.cycles);
  }
}

const args = process.argv.slice(2);
if(args.length < 1) {console.log('用法: node qvm2.js <字节码.qbc>');process.exit(1);}
const buf = fs.readFileSync(args[0]);

// Check magic
const magic = buf.toString('utf8', 0, 4);
if(magic !== 'QBC1') {
  // Try old format
  if(buf[0] === 0x14) {
    console.log('[QVM] 检测到旧格式QBC文件');
    const codeLen = buf.readUInt16LE(4);
    const code = Array.from(buf.slice(6, 6+codeLen));
    const spLen = buf.readUInt16LE(6+codeLen);
    const spData = Array.from(buf.slice(8+codeLen, 8+codeLen+spLen));
    console.log('加载旧格式: code_len='+codeLen+', sp_len='+spLen);
    const vm = new QVM2(code);
    vm.loadPool(spData);
    vm.extractFunctions();
    // Find main function
    const mainFunc = vm.funcs.get('main');
    if(mainFunc) {
      vm.pc = mainFunc.start;
      vm.run();
    } else {
      console.log('错误: 未找到main函数');
    }
    return;
  }
  console.log('[QVM] 无效的字节码格式: '+magic);
  process.exit(1);
}

const codeLen = buf.readUInt16LE(4);
const code = Array.from(buf.slice(6, 6+codeLen));
const spLen = buf.readUInt16LE(6+codeLen);
const spData = Array.from(buf.slice(8+codeLen, 8+codeLen+spLen));
console.log('加载: code_len='+codeLen+', sp_len='+spLen);
const vm = new QVM2(code);
vm.loadPool(spData);
vm.extractFunctions();
const mainFunc = vm.funcs.get('main');
if(!mainFunc) console.log('错误: 未找到main函数');
else {
  vm.pc = mainFunc.start;
  vm.run();
}