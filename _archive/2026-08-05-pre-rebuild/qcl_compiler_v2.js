#!/usr/bin/env node
const fs=require('fs');
const OP={
    NOP:0x00,PRINT:0x0B,STOP:0x0C,JUMP:0x0A,RETURN:0x0E,
    CALL:0x70,NATIVE_CALL:0x70,LOAD:0x22,STORE:0x21,DECL:0x6A,
    BC_FUNC_END:0xFE,FUNC_END:0x6F,
    IF_STMT:0x6C,ELSE_STMT:0x6D,WHILE_STMT:0x6E,BLOCK_END:0x6F,
    ADD:0x10,SUB:0x0D,MUL:0x0F,DIV:0x0E,
    EQ:0xA3,NE:0xA4,LT:0xA5,GT:0xA6,LE:0xA7,GE:0xA8,
    CONST_INT:0x78,CONST_STR:0x79
};
function bc_b(b){bc.push(b&0xFF)}
function bc_u16(v){bc.push(v&0xFF,(v>>8)&0xFF)}
function bc_u32(v){for(let i=0;i<4;i++)bc.push((v>>(i*8))&0xFF)}
let bc=[],block_stk=[],block_top=0,funcStack=[];
let stringPool=[],strMap={},varStack=[{}];
function addString(s){if(strMap[s]!==undefined)return strMap[s];const idx=stringPool.length;stringPool.push(s);strMap[s]=idx;return idx}
function emit_byte(op){bc_b(op)}
function emit_u16(v){bc_u16(v)}
function declareVar(name){varStack[varStack.length-1][name]=varStack.length-1}
function tokenize(line){
    const tokens=[];
    let i=0;
    while(i<line.length){
        if(line[i]===' ')i++;
        else if(/[\d.]/.test(line[i])){
            let num='';
            while(i<line.length&&/[\d.]/.test(line[i])){num+=line[i];i++}
            tokens.push({type:'number',val:parseFloat(num)});
        }else if(/[\w_]/.test(line[i])){
            let word='';
            while(i<line.length&&/[\w_]/.test(line[i])){word+=line[i];i++}
            if(word==='if')tokens.push({type:'id',val:'if'});
            else if(word==='else')tokens.push({type:'id',val:'else'});
            else if(word==='while')tokens.push({type:'id',val:'while'});
            else if(word==='def')tokens.push({type:'id',val:'def'});
            else if(word==='var')tokens.push({type:'id',val:'var'});
            else if(word==='return')tokens.push({type:'id',val:'return'});
            else if(word==='end')tokens.push({type:'id',val:'end'});
            else tokens.push({type:'id',val:word});
        }else if(line[i]==='"'){
            let str='';i++;
            while(i<line.length&&line[i]!=='"'){str+=line[i];i++}
            if(i<line.length)i++;
            tokens.push({type:'string',val:str});
        }else if('+=-*/<>!'.includes(line[i])){
            tokens.push({type:'op',val:line[i]});i++;
        }else if(line[i]===':'){tokens.push({type:'colon',val:':'});i++}
        else if(line[i]==='('){tokens.push({type:'lparen',val:'('});i++}
        else if(line[i]===')'){tokens.push({type:'rparen',val:')'});i++}
        else if(line[i]===','){tokens.push({type:'comma',val:','});i++}
        else if(line[i]==='#'){while(i<line.length&&line[i]!=='\n')i++}
        else i++;
    }
    tokens.push({type:'eof',val:''});
    return tokens;
}
function parseExpr(tokens,idx){
    // Simplified: just handle literals and identifiers
    const tok=tokens[idx];
    if(tok.type==='number'){bc_b(OP.CONST_INT);bc_u16(tok.val);return idx+1}
    if(tok.type==='string'){const sidx=addString(tok.val);bc_b(OP.CONST_STR);bc_u16(sidx);return idx+1}
    if(tok.type==='id'){const sidx=addString(tok.val);bc_b(OP.LOAD);bc_u16(sidx);return idx+1}
    return idx;
}
function parseStmt(tokens,idx){
    const tok=tokens[idx];
    if(tok.type==='id'&&tokens[idx+1]&&tokens[idx+1].val==='='){
        const sidx=addString(tok.val);idx+=2;
        idx=parseExpr(tokens,idx);
        bc_b(OP.STORE);bc_u16(sidx);
        return idx;
    }
    if(tok.type==='id'&&tokens[idx+1]&&tokens[idx+1].val==='('){
        const sidx=addString(tok.val);idx+=2;
        let nargs=0;
        while(tokens[idx].val!==')'){idx=parseExpr(tokens,idx);nargs++;if(tokens[idx].val===',')idx++}
        if(tokens[idx].val===')')idx++;
        bc_b(OP.NATIVE_CALL);bc_u16(sidx);bc_b(nargs);
        return idx;
    }
    if(tok.type==='id'&&tok.val==='return'){
        idx++;
        idx=parseExpr(tokens,idx);
        bc_b(OP.RETURN);
        return idx;
    }
    return idx;
}
function parseBlock(tokens,idx){
    while(idx<tokens.length&&tokens[idx].type!=='end'&&tokens[idx].type!=='eof'){
        idx=parseStmt(tokens,idx);
    }
    return idx;
}
function compile(input){
    const lines=input.split('\n');
    console.log('compile: '+lines.length+' lines');
    bc=[];block_stk=[];block_top=0;funcStack=[];
    stringPool=[];strMap={};varStack=[{}];
    
    // Add 'main' first so it gets index 0
    addString('main');
    
    // First pass: collect function definitions and their byte positions
    const funcDefs=[];
    const topLevelCode=[];
    let inFunc=false;
    let funcName='';
    let funcStart=-1;
    
    for(let i=0;i<lines.length;i++){
        const trimmed=lines[i].trim();
        if(trimmed===''||trimmed.startsWith('#'))continue;
        
        if(trimmed.startsWith('def ')){
            if(inFunc){
                console.log('ERROR: nested def');
                continue;
            }
            funcName=trimmed.substring(4).split('(')[0].trim();
            console.log('DEF at line '+(i+1)+': '+funcName);
            funcStart=topLevelCode.length;
            inFunc=true;
            continue;
        }
        
        if(trimmed==='end'&&inFunc){
            // Save function definition
            const funcCode=topLevelCode.slice(funcStart);
            funcDefs.push({name:funcName,code:funcCode});
            topLevelCode.length=funcStart;
            inFunc=false;
            funcName='';
            continue;
        }
        
        if(inFunc){
            topLevelCode.push(trimmed);
        }else{
            topLevelCode.push(trimmed);
        }
    }
    
    console.log('Functions found:',funcDefs.length);
    console.log('Top-level lines:',topLevelCode.length);
    
    // Now compile: first functions, then main wrapper
    block_stk[block_top++]='main_wrapper';
    
    // Compile functions first
    for(const func of funcDefs){
        const spIdx=addString(func.name);
        const params=[];
        const paramsMatch=func.name.match(/\(([^)]*)\)/);
        if(paramsMatch){
            const pStr=paramsMatch[1].trim();
            if(pStr)params.push(...pStr.split(',').map(p=>p.trim()).filter(p=>p));
        }
        const _len=func.name.length;
        bc_b(0x66);bc_u16(spIdx);bc_u16(_len);bc_u16(params.length);bc_b(0xFF);
        
        // Compile function body
        for(const stmt of func.code){
            const tokens=tokenize(stmt);
            let idx=0;
            while(idx<tokens.length&&tokens[idx].type!=='end'&&tokens[idx].type!=='eof'){
                idx=parseStmt(tokens,idx);
            }
        }
        bc_b(OP.BC_FUNC_END);bc_b(OP.FUNC_END);
    }
    
    // Compile top-level code (main body)
    for(const stmt of topLevelCode){
        const tokens=tokenize(stmt);
        let idx=0;
        while(idx<tokens.length&&tokens[idx].type!=='end'&&tokens[idx].type!=='eof'){
            idx=parseStmt(tokens,idx);
        }
    }
    
    // Close main wrapper
    if(block_top>0){
        block_top--;
        if(block_stk[block_top]==='main_wrapper'){
            // Insert main FUNC_DEF at beginning if not already there
            if(bc.length>0&&bc[0]!==0x66){
                const code=bc.slice();
                bc.length=0;
                bc_b(0x66);bc_u16(0);bc_u16(4);bc_u16(0);bc_b(0xFF);
                bc.push(...code);
            }
            bc_b(OP.BC_FUNC_END);bc_b(OP.FUNC_END);
            console.log("CLOSE MAIN WRAPPER");
        }
    }
    console.log('compile done: '+bc.length+' bytes');
}
function writeOutput(path){
    const buf=[];
    buf.push(0x14,0x00,0x00,0x00);
    const codeLen=bc.length;
    buf.push(codeLen&0xFF,(codeLen>>8)&0xFF);
    buf.push(...bc);
    let spData=[];
    for(const s of stringPool){
        spData.push(...Buffer.from(s,'utf8'));spData.push(0x00);
    }
    const spLen=spData.length;
    buf.push(spLen&0xFF,(spLen>>8)&0xFF);
    buf.push(...spData);
    fs.writeFileSync(path,Buffer.from(buf));
    console.log('output: '+codeLen+' bytes, pool: '+stringPool.length+' items');
}
const inputPath=process.argv[2],outputPath=process.argv[3];
if(!inputPath||!outputPath){console.error('用法: node qcl_compiler.js <输入.qentl> <输出.qbc>');process.exit(1);}
const input=fs.readFileSync(inputPath,'utf8');
compile(input);
writeOutput(outputPath);
