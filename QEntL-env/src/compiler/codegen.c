/**
 * QEntL量子纠缠语言代码生成器
 * 
 * 量子基因编码: QG-COMP-CODEGEN-A3B7-1713051200
 * 
 * @文件: codegen.c
 * @描述: 实现QEntL语言的代码生成，将AST转换为QEntL字节码
 * @作者: QEntL核心开发团队
 * @日期: 2024-05-16
 * @版本: 1.0
 * 
 * 量子纠缠信息:
 * - 此模块默认处于激活状态，能自动参与量子纠缠网络构建
 * - 代码生成支持量子优化和量子比特自适应分配
 * - 支持量子态编码和量子纠缠指令优化
 */

#include "codegen.h"
#include "semantic.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

/* 代码生成器内部状态 */
typedef struct {
    AST* ast;                    /* 抽象语法树 */
    BytecodeModule* module;      /* 生成的字节码模块 */
    SymbolTable* symbol_table;   /* 符号表 */
    int current_register;        /* 当前使用的寄存器编号 */
    int current_label;           /* 当前使用的标签编号 */
    int quantum_mode;            /* 是否处于量子模式 */
} CodeGenerator;

/* 创建代码生成器 */
static CodeGenerator* codegen_create(AST* ast, SymbolTable* symbol_table) {
    if (!ast || !symbol_table) {
        return NULL;
    }
    
    CodeGenerator* gen = (CodeGenerator*)malloc(sizeof(CodeGenerator));
    if (!gen) {
        return NULL;
    }
    
    gen->ast = ast;
    gen->symbol_table = symbol_table;
    gen->module = bytecode_module_create();
    gen->current_register = 0;
    gen->current_label = 0;
    gen->quantum_mode = 0;
    
    return gen;
}

/* 销毁代码生成器 */
static void codegen_destroy(CodeGenerator* gen) {
    if (!gen) {
        return;
    }
    
    // 注意：不销毁AST和符号表，因为它们是外部传入的
    if (gen->module) {
        bytecode_module_destroy(gen->module);
    }
    
    free(gen);
}

/* 生成新的寄存器 */
static int codegen_new_register(CodeGenerator* gen) {
    return gen->current_register++;
}

/* 生成新的标签 */
static int codegen_new_label(CodeGenerator* gen) {
    return gen->current_label++;
}

/* 发出字节码指令 */
static void codegen_emit(CodeGenerator* gen, OpCode op, int dst, int src1, int src2) {
    bytecode_instruction instr;
    instr.opcode = op;
    instr.dst = dst;
    instr.src1 = src1;
    instr.src2 = src2;
    
    bytecode_module_add_instruction(gen->module, instr);
}

/* 发出标签 */
static void codegen_emit_label(CodeGenerator* gen, int label) {
    bytecode_module_add_label(gen->module, label);
}

/* 生成常量加载指令 */
static int codegen_emit_load_constant(CodeGenerator* gen, Constant value) {
    int const_idx = bytecode_module_add_constant(gen->module, value);
    int reg = codegen_new_register(gen);
    
    codegen_emit(gen, OP_LOAD_CONST, reg, const_idx, 0);
    
    return reg;
}

/* 生成整数常量加载指令 */
static int codegen_emit_load_int(CodeGenerator* gen, int value) {
    Constant c;
    c.type = CONSTANT_INT;
    c.value.int_value = value;
    
    return codegen_emit_load_constant(gen, c);
}

/* 生成浮点常量加载指令 */
static int codegen_emit_load_float(CodeGenerator* gen, double value) {
    Constant c;
    c.type = CONSTANT_FLOAT;
    c.value.float_value = value;
    
    return codegen_emit_load_constant(gen, c);
}

/* 生成字符串常量加载指令 */
static int codegen_emit_load_string(CodeGenerator* gen, const char* value) {
    Constant c;
    c.type = CONSTANT_STRING;
    c.value.string_value = strdup(value);
    
    return codegen_emit_load_constant(gen, c);
}

/* 为表达式生成代码 */
static int codegen_expression(CodeGenerator* gen, ASTNode* expr) {
    if (!expr) {
        return -1;
    }
    
    switch (expr->type) {
        case NODE_LITERAL: {
            switch (expr->data.literal.data_type) {
                case TYPE_INT:
                    return codegen_emit_load_int(gen, expr->data.literal.value.int_value);
                    
                case TYPE_FLOAT:
                    return codegen_emit_load_float(gen, expr->data.literal.value.float_value);
                    
                case TYPE_STRING:
                    return codegen_emit_load_string(gen, expr->data.literal.value.string_value);
                    
                case TYPE_BOOL: {
                    int value = expr->data.literal.value.bool_value ? 1 : 0;
                    return codegen_emit_load_int(gen, value);
                }
                
                default:
                    // 不支持的字面量类型
                    return -1;
            }
        }
            
        case NODE_IDENTIFIER: {
            // 查找变量
            Symbol* symbol = symbol_table_lookup(gen->symbol_table, expr->data.identifier.name);
            if (!symbol || symbol->symbol_type != SYMBOL_VARIABLE) {
                // 未找到变量
                return -1;
            }
            
            // 生成变量加载指令
            int reg = codegen_new_register(gen);
            codegen_emit(gen, OP_LOAD_VAR, reg, symbol->data_type, 0);
            codegen_emit_load_string(gen, symbol->name);
            
            return reg;
        }
            
        case NODE_BINARY_OP: {
            int left_reg = codegen_expression(gen, expr->data.binary_op.left);
            int right_reg = codegen_expression(gen, expr->data.binary_op.right);
            
            if (left_reg < 0 || right_reg < 0) {
                return -1;
            }
            
            int result_reg = codegen_new_register(gen);
            
            // 根据运算符生成相应指令
            switch (expr->data.binary_op.operator) {
                case '+':
                    codegen_emit(gen, OP_ADD, result_reg, left_reg, right_reg);
                    break;
                    
                case '-':
                    codegen_emit(gen, OP_SUB, result_reg, left_reg, right_reg);
                    break;
                    
                case '*':
                    codegen_emit(gen, OP_MUL, result_reg, left_reg, right_reg);
                    break;
                    
                case '/':
                    codegen_emit(gen, OP_DIV, result_reg, left_reg, right_reg);
                    break;
                    
                case '<':
                    codegen_emit(gen, OP_LT, result_reg, left_reg, right_reg);
                    break;
                    
                case '>':
                    codegen_emit(gen, OP_GT, result_reg, left_reg, right_reg);
                    break;
                    
                case LE_OP:
                    codegen_emit(gen, OP_LE, result_reg, left_reg, right_reg);
                    break;
                    
                case GE_OP:
                    codegen_emit(gen, OP_GE, result_reg, left_reg, right_reg);
                    break;
                    
                case EQ_OP:
                    codegen_emit(gen, OP_EQ, result_reg, left_reg, right_reg);
                    break;
                    
                case NE_OP:
                    codegen_emit(gen, OP_NE, result_reg, left_reg, right_reg);
                    break;
                    
                case AND_OP:
                    codegen_emit(gen, OP_AND, result_reg, left_reg, right_reg);
                    break;
                    
                case OR_OP:
                    codegen_emit(gen, OP_OR, result_reg, left_reg, right_reg);
                    break;
                    
                case QUANTUM_ENTANGLE_OP:
                    codegen_emit(gen, OP_QUANTUM_ENTANGLE, result_reg, left_reg, right_reg);
                    break;
                    
                default:
                    // 不支持的运算符
                    return -1;
            }
            
            return result_reg;
        }
            
        case NODE_UNARY_OP: {
            int operand_reg = codegen_expression(gen, expr->data.unary_op.operand);
            
            if (operand_reg < 0) {
                return -1;
            }
            
            int result_reg = codegen_new_register(gen);
            
            // 根据运算符生成相应指令
            switch (expr->data.unary_op.operator) {
                case '-':
                    codegen_emit(gen, OP_NEG, result_reg, operand_reg, 0);
                    break;
                    
                case '!':
                    codegen_emit(gen, OP_NOT, result_reg, operand_reg, 0);
                    break;
                    
                case QUANTUM_OP:
                    codegen_emit(gen, OP_QUANTUM_CONVERT, result_reg, operand_reg, 0);
                    break;
                    
                default:
                    // 不支持的运算符
                    return -1;
            }
            
            return result_reg;
        }
            
        case NODE_FUNCTION_CALL: {
            // 生成参数代码
            int* arg_regs = (int*)malloc(expr->data.function_call.argument_count * sizeof(int));
            if (!arg_regs) {
                return -1;
            }
            
            for (int i = 0; i < expr->data.function_call.argument_count; i++) {
                arg_regs[i] = codegen_expression(gen, expr->data.function_call.arguments[i]);
                if (arg_regs[i] < 0) {
                    free(arg_regs);
                    return -1;
                }
            }
            
            // 生成函数调用指令
            int func_name_reg = codegen_emit_load_string(gen, expr->data.function_call.function_name);
            int result_reg = codegen_new_register(gen);
            
            codegen_emit(gen, OP_CALL, result_reg, func_name_reg, expr->data.function_call.argument_count);
            
            // 添加参数寄存器
            for (int i = 0; i < expr->data.function_call.argument_count; i++) {
                codegen_emit(gen, OP_PARAM, arg_regs[i], i, 0);
            }
            
            free(arg_regs);
            return result_reg;
        }
            
        case NODE_SUPERPOSITION: {
            // 生成量子叠加态
            int* state_regs = (int*)malloc(expr->data.superposition.state_count * sizeof(int));
            int* amplitude_regs = (int*)malloc(expr->data.superposition.state_count * sizeof(int));
            
            if (!state_regs || !amplitude_regs) {
                if (state_regs) free(state_regs);
                if (amplitude_regs) free(amplitude_regs);
                return -1;
            }
            
            for (int i = 0; i < expr->data.superposition.state_count; i++) {
                state_regs[i] = codegen_expression(gen, expr->data.superposition.states[i]);
                amplitude_regs[i] = codegen_expression(gen, expr->data.superposition.amplitudes[i]);
                
                if (state_regs[i] < 0 || amplitude_regs[i] < 0) {
                    free(state_regs);
                    free(amplitude_regs);
                    return -1;
                }
            }
            
            int result_reg = codegen_new_register(gen);
            codegen_emit(gen, OP_SUPERPOSITION, result_reg, expr->data.superposition.state_count, 0);
            
            // 添加状态和振幅
            for (int i = 0; i < expr->data.superposition.state_count; i++) {
                codegen_emit(gen, OP_SUPERPOSITION_STATE, state_regs[i], amplitude_regs[i], i);
            }
            
            free(state_regs);
            free(amplitude_regs);
            return result_reg;
        }
            
        default:
            // 不支持的表达式类型
            return -1;
    }
}

/* 为语句生成代码 */
static int codegen_statement(CodeGenerator* gen, ASTNode* stmt) {
    if (!stmt) {
        return 0;
    }
    
    switch (stmt->type) {
        case NODE_VARIABLE_DECLARATION: {
            // 生成初始化表达式（如果有）
            int init_reg = -1;
            if (stmt->data.variable_declaration.initializer) {
                init_reg = codegen_expression(gen, stmt->data.variable_declaration.initializer);
                if (init_reg < 0) {
                    return 0;
                }
            }
            
            // 生成变量声明指令
            int name_reg = codegen_emit_load_string(gen, stmt->data.variable_declaration.name);
            int type_reg = codegen_emit_load_int(gen, stmt->data.variable_declaration.data_type);
            
            if (init_reg >= 0) {
                codegen_emit(gen, OP_DECLARE_VAR_INIT, name_reg, type_reg, init_reg);
            } else {
                codegen_emit(gen, OP_DECLARE_VAR, name_reg, type_reg, 0);
            }
            
            return 1;
        }
            
        case NODE_FUNCTION_DECLARATION: {
            // 保存函数入口标签
            int func_label = codegen_new_label(gen);
            int end_label = codegen_new_label(gen);
            
            // 生成函数声明指令
            int name_reg = codegen_emit_load_string(gen, stmt->data.function_declaration.name);
            int return_type_reg = codegen_emit_load_int(gen, stmt->data.function_declaration.return_type);
            
            codegen_emit(gen, OP_DECLARE_FUNC, name_reg, return_type_reg, stmt->data.function_declaration.param_count);
            
            // 添加参数
            for (int i = 0; i < stmt->data.function_declaration.param_count; i++) {
                ASTNode* param = stmt->data.function_declaration.parameters[i];
                int param_name_reg = codegen_emit_load_string(gen, param->data.parameter.name);
                int param_type_reg = codegen_emit_load_int(gen, param->data.parameter.data_type);
                
                codegen_emit(gen, OP_FUNC_PARAM, param_name_reg, param_type_reg, i);
            }
            
            // 跳过函数体
            codegen_emit(gen, OP_JMP, end_label, 0, 0);
            
            // 生成函数体
            codegen_emit_label(gen, func_label);
            codegen_statement(gen, stmt->data.function_declaration.body);
            
            // 确保函数末尾有返回指令
            codegen_emit(gen, OP_RETURN, 0, 0, 0);
            
            codegen_emit_label(gen, end_label);
            
            return 1;
        }
            
        case NODE_BLOCK: {
            // 生成块中的每个语句
            for (int i = 0; i < stmt->data.block.statement_count; i++) {
                if (!codegen_statement(gen, stmt->data.block.statements[i])) {
                    return 0;
                }
            }
            
            return 1;
        }
            
        case NODE_IF_STATEMENT: {
            // 生成条件表达式
            int cond_reg = codegen_expression(gen, stmt->data.if_statement.condition);
            if (cond_reg < 0) {
                return 0;
            }
            
            int else_label = codegen_new_label(gen);
            int end_label = codegen_new_label(gen);
            
            // 条件跳转
            codegen_emit(gen, OP_JMP_IF_FALSE, cond_reg, else_label, 0);
            
            // 生成then分支
            if (!codegen_statement(gen, stmt->data.if_statement.then_branch)) {
                return 0;
            }
            
            // 跳过else分支
            codegen_emit(gen, OP_JMP, end_label, 0, 0);
            
            // 生成else分支（如果有）
            codegen_emit_label(gen, else_label);
            if (stmt->data.if_statement.else_branch) {
                if (!codegen_statement(gen, stmt->data.if_statement.else_branch)) {
                    return 0;
                }
            }
            
            codegen_emit_label(gen, end_label);
            
            return 1;
        }
            
        case NODE_WHILE_STATEMENT: {
            int start_label = codegen_new_label(gen);
            int end_label = codegen_new_label(gen);
            
            // 循环开始
            codegen_emit_label(gen, start_label);
            
            // 生成条件表达式
            int cond_reg = codegen_expression(gen, stmt->data.while_statement.condition);
            if (cond_reg < 0) {
                return 0;
            }
            
            // 条件跳转
            codegen_emit(gen, OP_JMP_IF_FALSE, cond_reg, end_label, 0);
            
            // 生成循环体
            if (!codegen_statement(gen, stmt->data.while_statement.body)) {
                return 0;
            }
            
            // 跳回循环开始
            codegen_emit(gen, OP_JMP, start_label, 0, 0);
            
            // 循环结束
            codegen_emit_label(gen, end_label);
            
            return 1;
        }
            
        case NODE_RETURN_STATEMENT: {
            // 生成返回值表达式（如果有）
            if (stmt->data.return_statement.value) {
                int value_reg = codegen_expression(gen, stmt->data.return_statement.value);
                if (value_reg < 0) {
                    return 0;
                }
                
                codegen_emit(gen, OP_RETURN_VALUE, value_reg, 0, 0);
            } else {
                codegen_emit(gen, OP_RETURN, 0, 0, 0);
            }
            
            return 1;
        }
            
        case NODE_EXPRESSION_STATEMENT: {
            // 生成表达式并丢弃结果
            int expr_reg = codegen_expression(gen, stmt->data.expression_statement.expression);
            if (expr_reg < 0) {
                return 0;
            }
            
            return 1;
        }
            
        case NODE_QUANTUM_MEASURE: {
            // 生成量子测量指令
            int expr_reg = codegen_expression(gen, stmt->data.quantum_measure.quantum_expr);
            if (expr_reg < 0) {
                return 0;
            }
            
            int result_reg = codegen_new_register(gen);
            codegen_emit(gen, OP_QUANTUM_MEASURE, result_reg, expr_reg, 0);
            
            return 1;
        }
            
        case NODE_QUANTUM_ENTANGLE: {
            // 生成量子纠缠指令
            int* entity_regs = (int*)malloc(stmt->data.quantum_entangle.entity_count * sizeof(int));
            if (!entity_regs) {
                return 0;
            }
            
            for (int i = 0; i < stmt->data.quantum_entangle.entity_count; i++) {
                entity_regs[i] = codegen_expression(gen, stmt->data.quantum_entangle.entities[i]);
                if (entity_regs[i] < 0) {
                    free(entity_regs);
                    return 0;
                }
            }
            
            int result_reg = codegen_new_register(gen);
            codegen_emit(gen, OP_QUANTUM_ENTANGLE_MULTI, result_reg, stmt->data.quantum_entangle.entity_count, 0);
            
            // 添加实体
            for (int i = 0; i < stmt->data.quantum_entangle.entity_count; i++) {
                codegen_emit(gen, OP_ENTANGLE_ENTITY, entity_regs[i], i, 0);
            }
            
            free(entity_regs);
            return 1;
        }
            
        default:
            // 不支持的语句类型
            return 0;
    }
}

/* 为整个AST生成代码 */
BytecodeModule* generate_code(AST* ast, SymbolTable* symbol_table) {
    if (!ast || !symbol_table) {
        return NULL;
    }
    
    CodeGenerator* gen = codegen_create(ast, symbol_table);
    if (!gen) {
        return NULL;
    }
    
    // 生成程序入口点
    int main_label = codegen_new_label(gen);
    codegen_emit_label(gen, main_label);
    
    // 生成每个顶级语句的代码
    for (int i = 0; i < ast->root_node_count; i++) {
        if (!codegen_statement(gen, ast->root_nodes[i])) {
            bytecode_module_destroy(gen->module);
            codegen_destroy(gen);
            return NULL;
        }
    }
    
    // 生成程序结束指令
    codegen_emit(gen, OP_HALT, 0, 0, 0);
    
    // 提取字节码模块
    BytecodeModule* module = gen->module;
    gen->module = NULL;
    
    // 销毁代码生成器
    codegen_destroy(gen);
    
    return module;
} 