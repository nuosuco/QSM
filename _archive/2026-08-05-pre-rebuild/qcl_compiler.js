#!/usr/bin/env node
const fs=require('fs');
const inPath=process.argv[2]||'qcl.qentl';
const code=fs.readFileSync(inPath,'utf8');
const lines=code.split('\n');
const OP={
    NOP:0,CONST_INT:0x78,CONST_STR:0x79,LOAD:0x22,STORE:0x21,DECL:0x6A,
    NATIVE_CALL:0x70,PRINT:0x0B,RETURN:0x0E,JUMP:0x0A,
    IF_STMT:0x6C,ELSE_STMT:0x6D,WHILE_STMT:0x6E,BLOCK_END:0x6F,
    FUNC_DEF:0x66,BC_FUNC_END:0xFE,
    ADD:0x10,SUB:0x11,MUL:0x0F,DIV:0x12,MOD:0x13,
    NOT:0x0D,AND:0xAB,OR:0xAC,ARRAY_ACCESS:0x68,ARRAY_SET:0x69,
    EQ:0xA9,NEQ:0xAA,LT:0xA5,GT:0xA6,LE:0xA7,GE:0xA8};
const opMap={'+':OP.ADD,'-':OP.SUB,'*':OP.MUL,'/':OP.DIV,'%':OP.MOD,'==':OP.EQ,'!=':OP.NEQ,
    '<':OP.LT,'>':OP.GT,'<=':OP.LE,'>=':OP.GE,'&&':OP.AND,'||':OP.OR,'!':OP.NOT};
let bc=[];let sp=[];let _toks=[];let _idx=0;
let vars={};let varStack=[{}];let funcStack=[];let block_stk=[];let block_top=0;
function addString(s){for(let i=0;i<sp.length;i++)if(sp[i]===s)return i;sp.push(s);return sp.length-1;}
function declareVar(name){vars[name]=0;varStack[varStack.length-1][name]=0;}
function tokenize(s){
    const toks=[];let i=0;
    while(i<s.length){
        if(s[i]===' '||s[i]==='\t'||s[i]==='\r'){i++;continue;}
        if(s[i]==='\n'){i++;continue;}
        if(s[i]==='#'){while(i<s.length&&s[i]!=='\n')i++;continue;}
        if(s[i]==='('){toks.push({type:'lparen',val:'('});i++;continue;}
        if(s[i]===')'){toks.push({type:'rparen',val:')'});i++;continue;}
        if(s[i]===','){toks.push({type:'comma',val:','});i++;continue;}
        if(s[i]===':'){toks.push({type:'colon',val:':'});i++;continue;}
        if(s[i]==='['){toks.push({type:'lbracket',val:'['});i++;continue;}
        if(s[i]===']'){toks.push({type:'rbracket',val:']'});i++;continue;}
        if(s[i]==='='&&s[i+1]!=='='){toks.push({type:'assign',val:'='});i++;continue;}
        if(s[i]==='"'||s[i]==="'"){
            const q=s[i];let str='';i++;
            while(i<s.length&&s[i]!==q){
                if(s[i]==='\\'){i++;if(i<s.length){const esc=s[i];i++;if(esc==='n')str+='\n';else if(esc==='t')str+='\t';else if(esc==='\\')str+='\\';else if(esc==='"')str+='"';else str+=esc;}}
                else str+=s[i++];
            }
            if(i<s.length)i++;
            toks.push({type:'str',val:str});continue;
        }
        if(/[0-9]/.test(s[i])){
            let n='';while(i<s.length&&/[0-9]/.test(s[i]))n+=s[i++];
            toks.push({type:'num',val:parseInt(n)});continue;
        }
        if(/[a-zA-Z_]/.test(s[i])){
            let w='';while(i<s.length&&/[a-zA-Z0-9_]/.test(s[i]))w+=s[i++];
            toks.push({type:'id',val:w});continue;
        }
        if(s[i]==='='&&s[i+1]==='='){toks.push({type:'op',val:'=='});i+=2;continue;}
        if(s[i]==='!'&&s[i+1]==='='){toks.push({type:'op',val:'!='});i+=2;continue;}
        if(s[i]==='<'&&s[i+1]==='='){toks.push({type:'op',val:'<='});i+=2;continue;}
        if(s[i]==='>'&&s[i+1]==='='){toks.push({type:'op',val:'>='});i+=2;continue;}
        if(s[i]==='&'&&s[i+1]==='&'){toks.push({type:'op',val:'&&'});i+=2;continue;}
        if(s[i]==='|'&&s[i+1]==='|'){toks.push({type:'op',val:'||'});i+=2;continue;}
        if('+-*/%<>!'.includes(s[i])){toks.push({type:'op',val:s[i]});i++;continue;}
        i++;
    }
    return toks;
}
function peekTok(){return _toks[_idx]||{type:'eof',val:'eof'};}
function nextTok(){return _toks[_idx++]||{type:'eof',val:'eof'};}
function parseExpr(prec){
    prec=prec||0;
    let guard=0;
    const tk=nextTok();
    if(tk.type==='eof'||tk.val===':'||tk.val===','||tk.val===')'||tk.type==='rbracket'){
        if(tk.val===':')_idx--;if(tk.val==='end')_idx--;if(tk.type==='rbracket')_idx--;
        return;
    }
    if(tk.type==='num'){bc_b(OP.CONST_INT);bc_u16(Number(tk.val));}
    else if(tk.type==='str'){const sidx=addString(tk.val);bc_b(OP.CONST_STR);bc_u16(sidx);}
    else if(tk.type==='id'){
        if(tk.val==='true'||tk.val==='false'){bc_b(OP.CONST_INT);bc_u16(tk.val==='true'?1:0);}
        else if(tk.val==='and'||tk.val==='or'){_idx--;return;}
        else if(peekTok().val==='('){
            nextTok();const sidx=addString(tk.val);let ac=0;
            while(peekTok().type!=='eof'&&peekTok().val!==')'&&peekTok().val!==':'){parseExpr(0);ac++;if(peekTok().val===',')nextTok();}
            if(peekTok().val===')')nextTok();
            bc_b(OP.NATIVE_CALL);bc_u16(sidx);bc_b(ac);
        }else if(peekTok().type==='lbracket'){
            nextTok();const sidx=addString(tk.val);bc_b(OP.LOAD);bc_u16(sidx);
            parseExpr(0);if(peekTok().type==='rbracket')nextTok();
            bc_b(OP.ARRAY_ACCESS);
        }else{const sidx=addString(tk.val);bc_b(OP.LOAD);bc_u16(sidx);}
    }
    else if(tk.type==='lparen'){parseExpr(0);if(peekTok().val===')')nextTok();}
    else if(tk.type==='op'){if(tk.val==='!'&&opMap[tk.val]){parseExpr(10);bc_b(opMap[tk.val]);}}
    // Binary operators with precedence: and<or<comparison<additive<multiplicative
    const precMap={'and':1,'or':0,'<':3,'>':3,'<=':3,'>=':3,'==':3,'!=':3,'+':4,'-':4,'*':5,'/':5,'%':5};
    while(true){
        if(++guard>200)break;
        const next=peekTok();
        let np=-1;
        if(next.val==='and'||next.val==='or')np=precMap[next.val];
        else if(next.type==='op'&&opMap[next.val])np=precMap[next.val];
        if(np===undefined||np<0)break;
        if(np<=prec)break;
        nextTok();
        if(next.val==='and'||next.val==='or'){
            // 'and'/'or' are id tokens, not op tokens
            parseExpr(np+1);
            bc_b(next.val==='and'?OP.AND:OP.OR);
        }else{
            parseExpr(np+1);
            bc_b(opMap[next.val]);
        }
    }
}
function bc_b(v){bc.push(v);}
function bc_u16(v){bc.push(v&0xFF);bc.push((v>>8)&0xFF);}
console.log('compile: '+lines.length+' lines');
addString('main');
for(let i=0;i<lines.length;i++){
    if(i%100===0)console.log('  line '+i);
    const trimmed=lines[i].trim();
    if(trimmed===''||trimmed.startsWith('#'))continue;
    _toks=tokenize(trimmed);_idx=0;
    const first=nextTok();
    if(first.val==='def'&&peekTok().type==='id'){
        const name=nextTok().val;console.log('  DEF '+(i+1)+': '+name);
        const params=[];let p=0;
        if(peekTok().val==='('){nextTok();while(peekTok().type!=='eof'&&peekTok().val!==')'){if(peekTok().type==='id')params.push(nextTok().val);else nextTok();}}
        if(peekTok().val===')')nextTok();if(peekTok().val===':')nextTok();
        addString(name);
        if(block_top>0&&block_stk[block_top-1]==='func'&&funcStack.length>0){
            bc_b(OP.BC_FUNC_END);block_top=funcStack.pop();
            if(varStack.length>1)varStack.pop();
        }
        funcStack.push(block_top);varStack.push({});
        params.forEach(p=>declareVar(p));
        const sidx=addString(name);
        bc_b(OP.FUNC_DEF);bc_u16(sidx);bc_u16(name.length);bc_u16(params.length);bc_b(0xFF);
        for(let pi=params.length-1;pi>=0;pi--){
            const psidx=addString(params[pi]);bc_b(OP.STORE);bc_u16(psidx);
        }
        block_stk[block_top++]='func';continue;
    }
    if(first.val==='end'){
        if(block_top>0){
            const bt=block_stk[block_top-1];
            const btType=typeof bt==='object'?bt.type:bt;
            block_top--;
            if(btType==='func'){bc_b(OP.BC_FUNC_END);}
            else if(btType==='while'){bc_b(OP.JUMP);bc_u16(bt.whilePos+8);bc_b(OP.BLOCK_END);}
            else if(btType==='else'){bc_b(OP.BLOCK_END);}
            else if(btType==='if'){bc_b(OP.BLOCK_END);}
        }
        continue;
    }
    if(first.type==='id'&&peekTok().val==='='){
        const sidx=addString(first.val);nextTok();parseExpr();bc_b(OP.STORE);bc_u16(sidx);continue;
    }
    if(first.val==='while'){
        const whilePos=bc.length;console.log('DEBUG whilePos='+whilePos+' bc.length='+bc.length+' bc[86]='+bc[86]+' bc[87]='+bc[87]);
        if(whilePos<95)console.log('DEBUG whilePos LAG: '+(95-whilePos)+' bytes behind');
        bc_b(OP.WHILE_STMT);bc_u16(0);
        parseExpr();if(peekTok().val===')')nextTok();if(peekTok().val===':')nextTok();
        const condLen=bc.length-(whilePos+3);
        bc[whilePos+1]=condLen&0xFF;
        bc[whilePos+2]=(condLen>>8)&0xFF;
        const jumpTarget = whilePos;
        block_stk[block_top++]={type:'while',whilePos:jumpTarget};
        continue;
    }
    if(first.type==='id'&&peekTok().type==='lparen'){
        if(first.val==='if'||first.val==='while'||first.val==='else'||first.val==='return'||first.val==='var'||first.val==='end'||first.val==='def')continue;
        nextTok();const sidx=addString(first.val);let ac=0;
        while(peekTok().type!=='eof'&&peekTok().val!==')'){parseExpr();ac++;if(peekTok().val===',')nextTok();}
        if(peekTok().val===')')nextTok();bc_b(OP.NATIVE_CALL);bc_u16(sidx);bc_b(ac);continue;
    }
    if(first.val==='return'){parseExpr();bc_b(OP.RETURN);continue;}
    if(first.val==='if'){
        const ifPos=bc.length;
        bc_b(OP.IF_STMT);bc_u16(0);
        parseExpr();if(peekTok().val===')')nextTok();if(peekTok().val===':')nextTok();
        const condLen=bc.length-(ifPos+3);
        bc[ifPos+1]=condLen&0xFF;
        bc[ifPos+2]=(condLen>>8)&0xFF;
        block_stk[block_top++]='if';
        continue;
    }
    if(first.val==='else'){bc_b(OP.ELSE_STMT);block_stk[block_top++]='else';continue;}
    if(first.val==='var'&&peekTok().type==='id'){
        const vname=nextTok().val;declareVar(vname);
        const sidx=addString(vname);
        if(peekTok().val==='['){nextTok();if(peekTok().type==='num')nextTok();if(peekTok().val===']')nextTok();}
        if(peekTok().val==='='){nextTok();parseExpr();bc_b(OP.STORE);bc_u16(sidx);}
        else{bc_b(OP.DECL);bc_u16(sidx);}
        continue;
    }
}
while(block_top>0){const bt=block_stk[block_top-1];block_top--;if(bt==='func')bc_b(OP.BC_FUNC_END);}
const codeBytes=bc.slice();const mainSidx=0;
console.log('DEBUG codeBytes.length='+codeBytes.length+' WHILE at codeBytes[87]='+codeBytes[87]+' codeBytes[95]='+codeBytes[95]);
bc=[];bc_b(OP.FUNC_DEF);bc_u16(mainSidx);bc_u16(codeBytes.length);bc_u16(0);bc_b(0xFF);
bc=bc.concat(codeBytes);
console.log('DEBUG final bc.length='+bc.length+' WHILE at bc[87]='+bc[87]+' bc[95]='+bc[95]+' bc[8+87]='+bc[8+87]);
const outPath=process.argv[3]||'output.qbc';
const poolSize=sp.reduce((a,s)=>a+s.length+1,0);
const buf=Buffer.alloc(6+bc.length+2+poolSize);
buf[0]=0x14;buf[4]=bc.length&0xFF;buf[5]=(bc.length>>8)&0xFF;
for(let i=0;i<bc.length;i++)buf[6+i]=bc[i];
const poolOff=6+bc.length;buf[poolOff]=poolSize&0xFF;buf[poolOff+1]=(poolSize>>8)&0xFF;
let pos=poolOff+2;sp.forEach(s=>{for(let j=0;j<s.length;j++){buf[pos]=s.charCodeAt(j);pos++;}buf[pos]=0;pos++;});
fs.writeFileSync(outPath,buf);
console.log('compile done: '+bc.length+' bytes\noutput: '+bc.length+' bytes, pool: '+sp.length+' items');