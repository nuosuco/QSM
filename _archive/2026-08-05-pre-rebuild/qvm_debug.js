#!/usr/bin/env node
const fs=require('fs');
const OP={
    NOP:0x00,PRINT:0x0B,STOP:0x0C,JUMP:0x0A,RETURN:0x0E,
    CALL:0x70,NATIVE_CALL:0x70,LOAD:0x22,STORE:0x21,DECL:0x6A,
    BC_FUNC_END:0xFE,FUNC_END:0x67,BLOCK_END:0x6F,
    IF_STMT:0x6C,ELSE_STMT:0x6D,WHILE_STMT:0x6E,
    FUNC_DEF:0x66,CONST_INT:0x78,CONST_STR:0x79
};
const builtins={};
builtins.printf=function(a,vm){process.stdout.write(a.map(x=>typeof x==='string'?x.replace(/\\n/g,'\n'):x).join(' '));};
builtins.file_read=function(a,vm){if(a.length>0)return fs.readFileSync(a[0],'utf8');return '';};
builtins.file_write=function(a,vm){if(a.length>1)fs.writeFileSync(a[0],a[1]);return 0;};
builtins.str_len=function(a){return typeof a[0]==='string'?a[0].length:0;};
builtins.str_sub=function(a){const s=a[0];const st=a[1]||0;const en=a[2]||s.length;if(typeof s==='string')return s.substring(st,en);return '';};
builtins.str_find=function(a){const s=a[0];const sub=a[1];if(typeof s==='string'&&typeof sub==='string')return s.indexOf(sub);return -1;};
builtins.ord=function(a){if(typeof a[0]==='string'&&a[0].length>0)return a[0].charCodeAt(0);return 0;};
builtins.chr=function(a){return String.fromCharCode(a[0]||0);};
builtins.to_int=function(a){return parseInt(a[0])||0;};
builtins.exit=function(){process.exit(0);};

class QVM{
    constructor(code,spData){
        this.code=code;
        this.spData=spData;
        this.pc=0;
        this.stack=[];
        this.vars={};
        this.callStack=[];
        this.running=true;
        this.cycles=0;
        this.funcs={};
    }
    readStrIdx(){
        const idx=this.code[this.pc]|(this.code[this.pc+1]<<8);
        this.pc+=2;
        return idx;
    }
    readStrFromPool(idx){
        let count=0,pos=0;
        while(pos<this.spData.length&&count<idx){
            while(pos<this.spData.length&&this.spData[pos]!==0)pos++;
            pos++;count++;
        }
        let s='';
        while(pos<this.spData.length&&this.spData[pos]!==0){s+=String.fromCharCode(this.spData[pos]);pos++;}
        return s;
    }
    getVar(name){
        if(typeof name==='number'){
            if(name<this.vars.length) return this.vars[name]||0;
            return 0;
        }
        return this.vars[name]||0;
    }
    skipToElseOrEnd(){
        let depth=1;
        while(this.pc<this.code.length&&depth>0){
            const op=this.code[this.pc];this.pc++;
            if(op===0x6c){const cl=this.code[this.pc]|(this.code[this.pc+1]<<8);this.pc+=2+cl;}
            else if(op===0x6e){const cl=this.code[this.pc]|(this.code[this.pc+1]<<8);this.pc+=2+cl;}
            else if(op===0x6d)depth++;
            else if(op===0x6f)depth--;
        }
    }
    extractFunctions(){
        let i=0;
        while(i<this.code.length){
            if(this.code[i]===0x66){
                const sidx=this.code[i+1]|(this.code[i+2]<<8);
                const flen=this.code[i+3]|(this.code[i+4]<<8);
                const paramCount=this.code[i+5]|(this.code[i+6]<<8);
                i+=7;
                if(this.code[i]===0xFF)i++;
                const funcName=this.readStrFromPool(sidx);
                this.funcs[funcName]={start:i,params:[]};
                if(funcName==='main')console.log("[extract] main func found at start="+i);
                if(funcName!=='main'&&funcName!=='')console.log("[extract] func '"+funcName+"' at pos="+i);
                let depth=1;
                while(i<this.code.length&&depth>0){
                    const op=this.code[i];
                    if(op===0xFE){depth--;i++;}
                    else if(op===0x66){i+=7;if(this.code[i]===0xFF)i++;depth++;}
                    else if(op===0x67){i++;if(depth<=0)break;}
                    else if(op===0x6c){const cl=this.code[i+1]|(this.code[i+2]<<8);i+=3+cl;}
                    else if(op===0x6e){const cl=this.code[i+1]|(this.code[i+2]<<8);i+=3+cl;}
                    else if(op===0x6d)i++;
                    else if(op===0x0a)i+=3;
                    else if(op===0x21||op===0x22||op===0x6a||op===0x79)i+=3;
                    else if(op===0x70)i+=4;
                    else if(op===0x78)i+=3;
                    else if(op===0x6b||op===0xFF||op===0x0E)i++;
                    else i++;
                }
                if(this.code[i]===0x67)i++;
            }else{
                const op=this.code[i];i++;
                if(op===0x0a)i+=2;
                else if(op===0x21||op===0x22||op===0x6a||op===0x79)i+=2;
                else if(op===0x70)i+=3;
                else if(op===0x78)i+=2;
                else if(op===0x6c){const cl=this.code[i]|(this.code[i+1]<<8);i+=2+cl;}
                else if(op===0x6e){const cl=this.code[i]|(this.code[i+1]<<8);i+=2+cl;}
            }
        }
        console.log("[extract] extractFunctions done");
    }
    run(){
        while(this.running){
            this.cycles++;
            const op=this.code[this.pc];
            this.pc++;
            switch(op){
                case 0x00:break;
                case 0x78:{const v=this.code[this.pc]|(this.code[this.pc+1]<<8);this.pc+=2;this.stack.push(v);break;}
                case 0x79:{const sidx=this.readStrIdx();this.stack.push(this.readStrFromPool(sidx));break;}
                case 0x22:{const n=this.readStrIdx();this.stack.push(this.getVar(n));break;}
                case 0x21:{const n=this.readStrIdx();if(this.stack.length>0)this.vars[n]=this.stack.pop();break;}
                case 0x6a:this.vars[this.readStrIdx()]=this.stack.length>0?this.stack.pop():0;break;
                case 0x6f:break;
                case 0x6b:if(this.callStack.length>0){const ret=this.callStack.pop();this.pc=ret.pc;}break;
                case 0x0e:if(this.callStack.length>0){const ret=this.callStack.pop();this.pc=ret.pc;}break;
                case 0x0d:{const b=this.stack.pop();const a=this.stack.pop();this.stack.push(a-b);break;}
                case 0x0e:{const b=this.stack.pop();const a=this.stack.pop();this.stack.push(b!==0?Math.floor(a/b):0);break;}
                case 0x0f:{const b=this.stack.pop();const a=this.stack.pop();this.stack.push(a*b);break;}
                case 0x10:{const b=this.stack.pop();const a=this.stack.pop();this.stack.push(a+b);break;}
                case 0x21:{const b=this.stack.pop();const a=this.stack.pop();this.stack.push(a||b?1:0);break;}
                case 0xa3:{const b=this.stack.pop();const a=this.stack.pop();this.stack.push(a===b?1:0);break;}
                case 0xa4:{const b=this.stack.pop();const a=this.stack.pop();this.stack.push(a!==b?1:0);break;}
                case 0xa5:{const b=this.stack.pop();const a=this.stack.pop();this.stack.push(a<b?1:0);break;}
                case 0xa6:{const b=this.stack.pop();const a=this.stack.pop();this.stack.push(a>b?1:0);break;}
                case 0xa7:{const b=this.stack.pop();const a=this.stack.pop();this.stack.push(a<=b?1:0);break;}
                case 0xa8:{const b=this.stack.pop();const a=this.stack.pop();this.stack.push(a>=b?1:0);break;}
                case 0x20:{const b=this.stack.pop();const a=this.stack.pop();this.stack.push(a&&b?1:0);break;}
                case 0x1e:{const a=this.stack.pop();this.stack.push(a?0:1);break;}
                case 0x6c:{
                    const codeLen=this.code[this.pc]|(this.code[this.pc+1]<<8);
                    const condStart=this.pc+2;
                    this.pc+=2+codeLen;
                    const savedPc=this.pc;
                    this.pc=condStart;
                    while(this.pc<condStart+codeLen){
                        this.cycles++;
                        const subOp=this.code[this.pc];this.pc++;
                        switch(subOp){
                            case 0x00:break;
                            case 0x78:{this.stack.push(this.code[this.pc]|(this.code[this.pc+1]<<8));this.pc+=2;break;}
                            case 0x79:this.stack.push(this.readStrIdx()||'');break;
                            case 0x22:{const n=this.readStrIdx();this.stack.push(this.getVar(n));break;}
                            case 0x21:this.readStrIdx();if(this.stack.length>0)this.stack.pop();break;
                            case 0x6a:this.vars[this.readStrIdx()]=this.stack.length>0?this.stack.pop():0;break;
                            case 0x6f:break;
                            case 0x6b:break;
                            case 0x70:{const fn=this.readStrIdx();const nargs=this.code[this.pc++];const a=[];for(let i=0;i<nargs&&this.stack.length>0;i++)a.unshift(this.stack.pop());if(builtins[fn]){const r=builtins[fn](a,this);if(r!==undefined)this.stack.push(r);}break;}
                            case 0x0d:{const b=this.stack.pop();const a=this.stack.pop();this.stack.push(a-b);break;}
                            case 0x0e:{const b=this.stack.pop();const a=this.stack.pop();this.stack.push(b!==0?Math.floor(a/b):0);break;}
                            case 0x0f:{const b=this.stack.pop();const a=this.stack.pop();this.stack.push(a*b);break;}
                            case 0x10:{const b=this.stack.pop();const a=this.stack.pop();this.stack.push(a+b);break;}
                            case 0xa3:{const b=this.stack.pop();const a=this.stack.pop();this.stack.push(a===b?1:0);break;}
                            case 0xa4:{const b=this.stack.pop();const a=this.stack.pop();this.stack.push(a!==b?1:0);break;}
                            case 0xa5:{const b=this.stack.pop();const a=this.stack.pop();this.stack.push(a<b?1:0);break;}
                            case 0xa6:{const b=this.stack.pop();const a=this.stack.pop();this.stack.push(a>b?1:0);break;}
                            case 0xa7:{const b=this.stack.pop();const a=this.stack.pop();this.stack.push(a<=b?1:0);break;}
                            case 0xa8:{const b=this.stack.pop();const a=this.stack.pop();this.stack.push(a>=b?1:0);break;}
                            case 0x20:{const b=this.stack.pop();const a=this.stack.pop();this.stack.push(a&&b?1:0);break;}
                            case 0x1e:{const a=this.stack.pop();this.stack.push(a?0:1);break;}
                            default:this.pc++;
                        }
                    }
                    this.pc=savedPc;
                    const cond=this.stack.length>0?this.stack.pop():0;
                    if(!cond)this.skipToElseOrEnd();
                    break;
                }
                case 0x0a:{this.pc=this.code[this.pc]|(this.code[this.pc+1]<<8);break;}
                case 0x6d:this.skipToElseOrEnd();break;
                case 0x6e:{
                    const condStart=this.pc+2;
                    const codeLen=this.code[this.pc]|(this.code[this.pc+1]<<8);
                    const bodyStart=this.pc+2+codeLen;
                    const whilePc=this.pc-1;
                    this.pc=condStart;
                    while(this.pc<condStart+codeLen){
                        this.cycles++;
                        const subOp=this.code[this.pc];this.pc++;
                        switch(subOp){
                            case 0x00:break;
                            case 0x78:{this.stack.push(this.code[this.pc]|(this.code[this.pc+1]<<8));this.pc+=2;break;}
                            case 0x79:this.stack.push(this.readStrIdx()||'');break;
                            case 0x22:{const n=this.readStrIdx();this.stack.push(this.getVar(n));break;}
                            case 0x21:this.readStrIdx();if(this.stack.length>0)this.stack.pop();break;
                            case 0x6a:this.vars[this.readStrIdx()]=this.stack.length>0?this.stack.pop():0;break;
                            case 0x6f:break;
                            case 0x6b:break;
                            case 0x70:{const fn=this.readStrIdx();const nargs=this.code[this.pc++];const a=[];for(let i=0;i<nargs&&this.stack.length>0;i++)a.unshift(this.stack.pop());if(builtins[fn]){const r=builtins[fn](a,this);if(r!==undefined)this.stack.push(r);}break;}
                            case 0x0d:{const b=this.stack.pop();const a=this.stack.pop();this.stack.push(a-b);break;}
                            case 0x0e:{const b=this.stack.pop();const a=this.stack.pop();this.stack.push(b!==0?Math.floor(a/b):0);break;}
                            case 0x0f:{const b=this.stack.pop();const a=this.stack.pop();this.stack.push(a*b);break;}
                            case 0x10:{const b=this.stack.pop();const a=this.stack.pop();this.stack.push(a+b);break;}
                            case 0xa3:{const b=this.stack.pop();const a=this.stack.pop();this.stack.push(a===b?1:0);break;}
                            case 0xa4:{const b=this.stack.pop();const a=this.stack.pop();this.stack.push(a!==b?1:0);break;}
                            case 0xa5:{const b=this.stack.pop();const a=this.stack.pop();this.stack.push(a<b?1:0);break;}
                            case 0xa6:{const b=this.stack.pop();const a=this.stack.pop();this.stack.push(a>b?1:0);break;}
                            case 0xa7:{const b=this.stack.pop();const a=this.stack.pop();this.stack.push(a<=b?1:0);break;}
                            case 0xa8:{const b=this.stack.pop();const a=this.stack.pop();this.stack.push(a>=b?1:0);break;}
                            case 0x20:{const b=this.stack.pop();const a=this.stack.pop();this.stack.push(a&&b?1:0);break;}
                            case 0x1e:{const a=this.stack.pop();this.stack.push(a?0:1);break;}
                            default:this.pc++;
                        }
                    }
                    const cond=this.stack.length>0?this.stack.pop():0;
                    if(!cond){this.pc=bodyStart;this.skipToElseOrEnd();}else{this.pc=bodyStart;}
                    break;
                }
                case 0x70:{
                    const fname=this.readStrIdx();
                    if(!this.funcs[fname]&&!builtins[fname]){this.pc++;break;}
                    const nargs=this.code[this.pc];this.pc++;
                    const args=[];
                    for(let i=0;i<nargs;i++)args.unshift(this.stack.length>0?this.stack.pop():0);
                    if(builtins[fname]){
                        if(fname==='printf')console.log('[DEBUG] printf called at pc='+(this.pc-1)+' args:',args.map(a=>typeof a==='string'?'\"'+a+'\":'+a.length:a));
                        const result=builtins[fname](args,this);
                        if(result!==undefined)this.stack.push(result);
                    }else if(this.funcs[fname]){
                        const func=this.funcs[fname];
                        for(let p=0;p<func.params.length&&p<args.length;p++){
                            const pname=this.readStrIdxFast(func.params[p]);
                            this.vars[pname]=args[p];
                        }
                        this.callStack.push({pc:this.pc,vars:{...this.vars}});
                        this.pc=func.start;
                    }
                    break;
                }
                case 0x66:{
                    const _fname=this.readStrFromPool(this.code[this.pc]|(this.code[this.pc+1]<<8));
                    console.log('[DEBUG] FUNC_DEF skip: "'+_fname+'" at pc='+(this.pc-1)+' cycles='+this.cycles);
                    let skip=6; // this.pc already incremented, so sidx at this.pc+0
                    if(this.code[this.pc+6]===0xFF)skip++;
                    let j=this.pc+skip;
                    while(j<this.code.length&&depth>0){
                        const op=this.code[j];
                        if(op===0xFE){depth--;if(depth===0){j++;break;}j++;}
                        else if(op===0x66){j+=7;if(this.code[j]===0xFF)j++;depth++;}
                        else if(op===0x67){j++;if(depth<=0)break;}
                        else if(op===0x6c){const cl=this.code[j+1]|(this.code[j+2]<<8);j+=3+cl;}
                        else if(op===0x6e){const cl=this.code[j+1]|(this.code[j+2]<<8);j+=3+cl;}
                        else if(op===0x6d)j++;
                        else if(op===0x0a)j+=3;
                        else if(op===0x21||op===0x22||op===0x6a||op===0x79)j+=3;
                        else if(op===0x70)j+=4;
                        else if(op===0x78)j+=3;
                        else if(op===0x6b||op===0xFF||op===0x0E)j++;
                        else j++;
                    }
                        else if(op===0x67){j++;if(depth<=0)break;}
                        else if(op===0x6c){const cl=this.code[j+1]|(this.code[j+2]<<8);j+=3+cl;}
                        else if(op===0x6e){const cl=this.code[j+1]|(this.code[j+2]<<8);j+=3+cl;}
                        else if(op===0x6d)j++;
                        else if(op===0x0a)j+=3;
                        else if(op===0x21||op===0x22||op===0x6a||op===0x79)j+=3;
                        else if(op===0x70)j+=4;
                        else if(op===0x78)j+=3;
                        else if(op===0x6b||op===0xFF||op===0x0E)j++;
                        else j++;
                    }
                    this.pc=j;
                    if(this.code[this.pc]===0x67)this.pc++;
                    console.log('[DEBUG] FUNC_DEF skip done: pc='+this.pc+' cycles='+this.cycles);
                    break;
                }
                case 0xFE:{
                    console.log('[DEBUG] BC_FUNC_END at pc='+(this.pc-1)+' cycles='+this.cycles+' callStack='+this.callStack.length);
                    if(this.callStack.length>0){
                        const ret=this.callStack.pop();
                        this.pc=ret.pc;
                    }else{
                        this.running=false;
                    }
                    break;
                }
                default:
                    console.log('[QVM] 未知opcode: 0x'+op.toString(16)+' (pos='+(this.pc-1)+')');
                    this.running=false;
                    break;
            }
        }
        console.log('[QVM] 执行完成: '+this.cycles+' 周期');
    }
}

const args=process.argv.slice(2);
if(args.length<1){console.log('用法: node qvm_sim.js <字节码.qbc>');process.exit(1);}
const buf=fs.readFileSync(args[0]);
const magic=buf[0];
if(magic!==0x14){console.log('[QVM] 无效的字节码格式');process.exit(1);}
const codeLen=buf.readUInt16LE(4);
const code=Array.from(buf.slice(6,6+codeLen));
const spLen=buf.readUInt16LE(6+codeLen);
const spData=Array.from(buf.slice(8+codeLen,8+codeLen+spLen));
console.log('[QVM] 加载QEntL字节码: code_len='+codeLen+', sp_len='+spLen);
const vm=new QVM(code,spData);
vm.extractFunctions();
const mainFunc=vm.funcs['main'];
if(!mainFunc)console.log('错误: 未找到main函数');
else vm.pc=mainFunc.start;
vm.run();