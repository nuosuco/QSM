/**
 * QEntL量子纠缠语言语义分析器
 * 
 * 量子基因编码: QG-COMP-SEM-A2B5-1713051200
 * 
 * @文件: semantic.c
 * @描述: 实现QEntL语言的语义分析，进行类型检查、作用域分析等
 * @作者: QEntL核心开发团队
 * @日期: 2024-05-16
 * @版本: 1.0
 * 
 * 量子纠缠信息:
 * - 此模块默认处于激活状态，能自动参与量子纠缠网络构建
 * - 语义分析支持量子叠加分析和量子基因表达式验证
 * - 能分析量子纠缠链接的合法性和资源消耗
 */

#include "semantic.h"
#include "parser.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdarg.h>

/* 语义分析器内部状态 */
typedef struct {
    AST* ast;                     /* 语法分析生成的抽象语法树 */
    SymbolTable* global_scope;    /* 全局符号表 */
    SymbolTable* current_scope;   /* 当前作用域符号表 */
    ErrorList* errors;            /* 语义错误列表 */
    int quantum_entanglement_level; /* 量子纠缠级别 */
    int in_quantum_context;       /* 是否在量子上下文中 */
} SemanticAnalyzer;

/* 创建一个新的语义分析器 */
SemanticAnalyzer* semantic_analyzer_create(AST* ast) {
    if (!ast) {
        return NULL;
    }
    
    SemanticAnalyzer* analyzer = (SemanticAnalyzer*)malloc(sizeof(SemanticAnalyzer));
    if (!analyzer) {
        return NULL;
    }
    
    analyzer->ast = ast;
    analyzer->global_scope = symbol_table_create(NULL);
    analyzer->current_scope = analyzer->global_scope;
    analyzer->errors = error_list_create();
    analyzer->quantum_entanglement_level = 0;
    analyzer->in_quantum_context = 0;
    
    return analyzer;
}

/* 销毁语义分析器 */
void semantic_analyzer_destroy(SemanticAnalyzer* analyzer) {
    if (!analyzer) {
        return;
    }
    
    symbol_table_destroy(analyzer->global_scope);
    error_list_destroy(analyzer->errors);
    free(analyzer);
}

/* 记录语义错误 */
static void semantic_error(SemanticAnalyzer* analyzer, const char* format, ...) {
    va_list args;
    va_start(args, format);
    
    char buffer[1024];
    vsnprintf(buffer, sizeof(buffer), format, args);
    
    error_list_add(analyzer->errors, buffer);
    
    va_end(args);
}

/* 检查变量是否已在当前作用域中声明 */
static int is_variable_declared(SemanticAnalyzer* analyzer, const char* name) {
    Symbol* symbol = symbol_table_lookup(analyzer->current_scope, name);
    return symbol != NULL;
}

/* 检查类型兼容性 */
static int are_types_compatible(DataType type1, DataType type2) {
    if (type1 == type2) {
        return 1;
    }
    
    // 量子类型和经典类型之间的特殊转换规则
    if ((type1 == TYPE_QUANTUM_INT && type2 == TYPE_INT) ||
        (type1 == TYPE_INT && type2 == TYPE_QUANTUM_INT) ||
        (type1 == TYPE_QUANTUM_FLOAT && type2 == TYPE_FLOAT) ||
        (type1 == TYPE_FLOAT && type2 == TYPE_QUANTUM_FLOAT)) {
        return 1;
    }
    
    // 量子叠加态可以与其基础类型兼容
    if (type1 == TYPE_SUPERPOSITION) {
        return 1;
    }
    
    return 0;
}

/* 分析表达式，返回表达式的类型 */
static DataType analyze_expression(SemanticAnalyzer* analyzer, ASTNode* expr) {
    if (!expr) {
        return TYPE_UNKNOWN;
    }
    
    switch (expr->type) {
        case NODE_LITERAL:
            return expr->data.literal.data_type;
            
        case NODE_IDENTIFIER: {
            const char* name = expr->data.identifier.name;
            Symbol* symbol = symbol_table_lookup(analyzer->current_scope, name);
            
            if (!symbol) {
                semantic_error(analyzer, "未定义的标识符 '%s'", name);
                return TYPE_UNKNOWN;
            }
            
            return symbol->data_type;
        }
            
        case NODE_BINARY_OP: {
            DataType left_type = analyze_expression(analyzer, expr->data.binary_op.left);
            DataType right_type = analyze_expression(analyzer, expr->data.binary_op.right);
            
            // 运算符的语义检查
            switch (expr->data.binary_op.operator) {
                case '+':
                case '-':
                case '*':
                case '/':
                    // 数值运算
                    if ((left_type == TYPE_INT || left_type == TYPE_FLOAT || 
                         left_type == TYPE_QUANTUM_INT || left_type == TYPE_QUANTUM_FLOAT) &&
                        (right_type == TYPE_INT || right_type == TYPE_FLOAT || 
                         right_type == TYPE_QUANTUM_INT || right_type == TYPE_QUANTUM_FLOAT)) {
                        
                        // 如果有任何量子类型，结果就是量子类型
                        if (left_type == TYPE_QUANTUM_INT || left_type == TYPE_QUANTUM_FLOAT ||
                            right_type == TYPE_QUANTUM_INT || right_type == TYPE_QUANTUM_FLOAT) {
                            
                            if (left_type == TYPE_QUANTUM_FLOAT || right_type == TYPE_QUANTUM_FLOAT ||
                                left_type == TYPE_FLOAT || right_type == TYPE_FLOAT) {
                                return TYPE_QUANTUM_FLOAT;
                            } else {
                                return TYPE_QUANTUM_INT;
                            }
                        } else {
                            if (left_type == TYPE_FLOAT || right_type == TYPE_FLOAT) {
                                return TYPE_FLOAT;
                            } else {
                                return TYPE_INT;
                            }
                        }
                    } else {
                        semantic_error(analyzer, "算术运算的操作数必须是数值类型");
                        return TYPE_UNKNOWN;
                    }
                    
                case '&':
                case '|':
                case '^':
                    // 位运算
                    if ((left_type == TYPE_INT || left_type == TYPE_QUANTUM_INT) &&
                        (right_type == TYPE_INT || right_type == TYPE_QUANTUM_INT)) {
                        if (left_type == TYPE_QUANTUM_INT || right_type == TYPE_QUANTUM_INT) {
                            return TYPE_QUANTUM_INT;
                        } else {
                            return TYPE_INT;
                        }
                    } else {
                        semantic_error(analyzer, "位运算的操作数必须是整数类型");
                        return TYPE_UNKNOWN;
                    }
                    
                case '<':
                case '>':
                case LE_OP:
                case GE_OP:
                case EQ_OP:
                case NE_OP:
                    // 比较运算
                    if (are_types_compatible(left_type, right_type)) {
                        if (left_type == TYPE_QUANTUM_INT || left_type == TYPE_QUANTUM_FLOAT ||
                            right_type == TYPE_QUANTUM_INT || right_type == TYPE_QUANTUM_FLOAT) {
                            return TYPE_QUANTUM_BOOL;
                        } else {
                            return TYPE_BOOL;
                        }
                    } else {
                        semantic_error(analyzer, "比较运算的操作数类型不兼容");
                        return TYPE_UNKNOWN;
                    }
                    
                case AND_OP:
                case OR_OP:
                    // 逻辑运算
                    if ((left_type == TYPE_BOOL || left_type == TYPE_QUANTUM_BOOL) &&
                        (right_type == TYPE_BOOL || right_type == TYPE_QUANTUM_BOOL)) {
                        if (left_type == TYPE_QUANTUM_BOOL || right_type == TYPE_QUANTUM_BOOL) {
                            return TYPE_QUANTUM_BOOL;
                        } else {
                            return TYPE_BOOL;
                        }
                    } else {
                        semantic_error(analyzer, "逻辑运算的操作数必须是布尔类型");
                        return TYPE_UNKNOWN;
                    }
                    
                case QUANTUM_ENTANGLE_OP:
                    // 量子纠缠运算符
                    analyzer->quantum_entanglement_level++;
                    if (analyzer->quantum_entanglement_level > 10) {
                        semantic_error(analyzer, "量子纠缠嵌套级别过深");
                    }
                    return TYPE_ENTANGLEMENT;
                    
                default:
                    semantic_error(analyzer, "不支持的二元运算符");
                    return TYPE_UNKNOWN;
            }
        }
            
        case NODE_UNARY_OP: {
            DataType operand_type = analyze_expression(analyzer, expr->data.unary_op.operand);
            
            switch (expr->data.unary_op.operator) {
                case '-':
                    if (operand_type == TYPE_INT || operand_type == TYPE_FLOAT) {
                        return operand_type;
                    } else if (operand_type == TYPE_QUANTUM_INT) {
                        return TYPE_QUANTUM_INT;
                    } else if (operand_type == TYPE_QUANTUM_FLOAT) {
                        return TYPE_QUANTUM_FLOAT;
                    } else {
                        semantic_error(analyzer, "一元负运算符的操作数必须是数值类型");
                        return TYPE_UNKNOWN;
                    }
                    
                case '!':
                    if (operand_type == TYPE_BOOL) {
                        return TYPE_BOOL;
                    } else if (operand_type == TYPE_QUANTUM_BOOL) {
                        return TYPE_QUANTUM_BOOL;
                    } else {
                        semantic_error(analyzer, "逻辑非运算符的操作数必须是布尔类型");
                        return TYPE_UNKNOWN;
                    }
                    
                case QUANTUM_OP:
                    analyzer->in_quantum_context = 1;
                    if (operand_type == TYPE_INT) {
                        return TYPE_QUANTUM_INT;
                    } else if (operand_type == TYPE_FLOAT) {
                        return TYPE_QUANTUM_FLOAT;
                    } else if (operand_type == TYPE_BOOL) {
                        return TYPE_QUANTUM_BOOL;
                    } else if (operand_type == TYPE_STRING) {
                        return TYPE_QUANTUM_STRING;
                    } else {
                        semantic_error(analyzer, "量子运算符不能应用于此类型");
                        return TYPE_UNKNOWN;
                    }
                    
                default:
                    semantic_error(analyzer, "不支持的一元运算符");
                    return TYPE_UNKNOWN;
            }
        }
            
        case NODE_FUNCTION_CALL: {
            const char* func_name = expr->data.function_call.function_name;
            Symbol* func_symbol = symbol_table_lookup(analyzer->current_scope, func_name);
            
            if (!func_symbol || func_symbol->symbol_type != SYMBOL_FUNCTION) {
                semantic_error(analyzer, "未定义的函数 '%s'", func_name);
                return TYPE_UNKNOWN;
            }
            
            // 检查参数数量
            if (func_symbol->data.function.param_count != expr->data.function_call.argument_count) {
                semantic_error(analyzer, "函数 '%s' 需要 %d 个参数，但提供了 %d 个",
                              func_name, func_symbol->data.function.param_count,
                              expr->data.function_call.argument_count);
            }
            
            // 检查参数类型
            for (int i = 0; i < expr->data.function_call.argument_count && 
                 i < func_symbol->data.function.param_count; i++) {
                DataType arg_type = analyze_expression(analyzer, expr->data.function_call.arguments[i]);
                DataType param_type = func_symbol->data.function.param_types[i];
                
                if (!are_types_compatible(arg_type, param_type)) {
                    semantic_error(analyzer, "函数 '%s' 的第 %d 个参数类型不匹配", func_name, i + 1);
                }
            }
            
            return func_symbol->data.function.return_type;
        }
            
        case NODE_SUPERPOSITION: {
            // 分析叠加态的每个分支
            for (int i = 0; i < expr->data.superposition.state_count; i++) {
                analyze_expression(analyzer, expr->data.superposition.states[i]);
                analyze_expression(analyzer, expr->data.superposition.amplitudes[i]);
            }
            
            return TYPE_SUPERPOSITION;
        }
            
        default:
            semantic_error(analyzer, "无法分析未知类型的表达式");
            return TYPE_UNKNOWN;
    }
}

/* 分析变量声明 */
static void analyze_variable_declaration(SemanticAnalyzer* analyzer, ASTNode* node) {
    if (!node || node->type != NODE_VARIABLE_DECLARATION) {
        return;
    }
    
    const char* var_name = node->data.variable_declaration.name;
    DataType var_type = node->data.variable_declaration.data_type;
    
    // 检查变量是否已声明
    if (is_variable_declared(analyzer, var_name)) {
        semantic_error(analyzer, "变量 '%s' 已在当前作用域中声明", var_name);
        return;
    }
    
    // 如果有初始化表达式，分析其类型
    if (node->data.variable_declaration.initializer) {
        DataType init_type = analyze_expression(analyzer, node->data.variable_declaration.initializer);
        
        // 检查初始化表达式类型与变量类型的兼容性
        if (!are_types_compatible(var_type, init_type)) {
            semantic_error(analyzer, "变量 '%s' 的初始化表达式类型不兼容", var_name);
        }
    }
    
    // 添加变量到符号表
    Symbol* symbol = symbol_create_variable(var_name, var_type);
    symbol_table_insert(analyzer->current_scope, symbol);
}

/* 分析函数声明 */
static void analyze_function_declaration(SemanticAnalyzer* analyzer, ASTNode* node) {
    if (!node || node->type != NODE_FUNCTION_DECLARATION) {
        return;
    }
    
    const char* func_name = node->data.function_declaration.name;
    DataType return_type = node->data.function_declaration.return_type;
    
    // 检查函数是否已声明
    if (is_variable_declared(analyzer, func_name)) {
        semantic_error(analyzer, "函数 '%s' 已在当前作用域中声明", func_name);
        return;
    }
    
    // 创建函数符号
    Symbol* func_symbol = symbol_create_function(func_name, return_type);
    
    // 添加参数类型信息
    for (int i = 0; i < node->data.function_declaration.param_count; i++) {
        ASTNode* param_node = node->data.function_declaration.parameters[i];
        const char* param_name = param_node->data.parameter.name;
        DataType param_type = param_node->data.parameter.data_type;
        
        symbol_function_add_parameter(func_symbol, param_type);
    }
    
    // 添加函数到符号表
    symbol_table_insert(analyzer->current_scope, func_symbol);
    
    // 创建新的作用域用于函数体
    SymbolTable* function_scope = symbol_table_create(analyzer->current_scope);
    analyzer->current_scope = function_scope;
    
    // 添加参数到函数作用域
    for (int i = 0; i < node->data.function_declaration.param_count; i++) {
        ASTNode* param_node = node->data.function_declaration.parameters[i];
        const char* param_name = param_node->data.parameter.name;
        DataType param_type = param_node->data.parameter.data_type;
        
        Symbol* param_symbol = symbol_create_variable(param_name, param_type);
        symbol_table_insert(analyzer->current_scope, param_symbol);
    }
    
    // 分析函数体
    analyze_statement(analyzer, node->data.function_declaration.body);
    
    // 恢复到上一个作用域
    analyzer->current_scope = analyzer->current_scope->parent;
}

/* 分析语句 */
static void analyze_statement(SemanticAnalyzer* analyzer, ASTNode* node) {
    if (!node) {
        return;
    }
    
    switch (node->type) {
        case NODE_VARIABLE_DECLARATION:
            analyze_variable_declaration(analyzer, node);
            break;
            
        case NODE_FUNCTION_DECLARATION:
            analyze_function_declaration(analyzer, node);
            break;
            
        case NODE_BLOCK: {
            // 创建新的作用域
            SymbolTable* block_scope = symbol_table_create(analyzer->current_scope);
            analyzer->current_scope = block_scope;
            
            // 分析块中的每个语句
            for (int i = 0; i < node->data.block.statement_count; i++) {
                analyze_statement(analyzer, node->data.block.statements[i]);
            }
            
            // 恢复到上一个作用域
            analyzer->current_scope = analyzer->current_scope->parent;
            break;
        }
            
        case NODE_IF_STATEMENT: {
            // 分析条件表达式
            DataType cond_type = analyze_expression(analyzer, node->data.if_statement.condition);
            if (cond_type != TYPE_BOOL && cond_type != TYPE_QUANTUM_BOOL) {
                semantic_error(analyzer, "if语句的条件必须是布尔类型或量子布尔类型");
            }
            
            // 分析if分支
            analyze_statement(analyzer, node->data.if_statement.then_branch);
            
            // 分析else分支（如果有）
            if (node->data.if_statement.else_branch) {
                analyze_statement(analyzer, node->data.if_statement.else_branch);
            }
            break;
        }
            
        case NODE_WHILE_STATEMENT: {
            // 分析条件表达式
            DataType cond_type = analyze_expression(analyzer, node->data.while_statement.condition);
            if (cond_type != TYPE_BOOL && cond_type != TYPE_QUANTUM_BOOL) {
                semantic_error(analyzer, "while语句的条件必须是布尔类型或量子布尔类型");
            }
            
            // 分析循环体
            analyze_statement(analyzer, node->data.while_statement.body);
            break;
        }
            
        case NODE_RETURN_STATEMENT: {
            // 分析返回表达式的类型
            DataType return_type = TYPE_VOID;
            if (node->data.return_statement.value) {
                return_type = analyze_expression(analyzer, node->data.return_statement.value);
            }
            
            // 检查是否在函数内部
            if (!analyzer->current_scope->parent) {
                semantic_error(analyzer, "return语句必须在函数内部使用");
                break;
            }
            
            // 获取当前函数的返回类型
            // 注意：这需要一个额外的机制来跟踪当前函数的返回类型
            // 这里简化处理，假设我们有一个方法可以获取当前函数的返回类型
            DataType func_return_type = get_current_function_return_type(analyzer);
            
            if (!are_types_compatible(func_return_type, return_type)) {
                semantic_error(analyzer, "函数返回类型与return语句类型不兼容");
            }
            break;
        }
            
        case NODE_EXPRESSION_STATEMENT:
            analyze_expression(analyzer, node->data.expression_statement.expression);
            break;
            
        case NODE_QUANTUM_MEASURE: {
            // 分析要测量的量子表达式
            DataType expr_type = analyze_expression(analyzer, node->data.quantum_measure.quantum_expr);
            
            // 检查是否是量子类型
            if (expr_type != TYPE_QUANTUM_INT && expr_type != TYPE_QUANTUM_FLOAT && 
                expr_type != TYPE_QUANTUM_BOOL && expr_type != TYPE_QUANTUM_STRING &&
                expr_type != TYPE_SUPERPOSITION && expr_type != TYPE_ENTANGLEMENT) {
                semantic_error(analyzer, "measure语句只能应用于量子类型");
            }
            break;
        }
            
        case NODE_QUANTUM_ENTANGLE: {
            // 分析要纠缠的量子表达式
            for (int i = 0; i < node->data.quantum_entangle.entity_count; i++) {
                DataType entity_type = analyze_expression(analyzer, node->data.quantum_entangle.entities[i]);
                
                if (entity_type != TYPE_QUANTUM_INT && entity_type != TYPE_QUANTUM_FLOAT && 
                    entity_type != TYPE_QUANTUM_BOOL && entity_type != TYPE_QUANTUM_STRING &&
                    entity_type != TYPE_SUPERPOSITION) {
                    semantic_error(analyzer, "entangle语句只能应用于量子类型");
                }
            }
            break;
        }
            
        default:
            semantic_error(analyzer, "未知语句类型");
            break;
    }
}

/* 获取当前函数的返回类型（辅助函数，简化实现） */
static DataType get_current_function_return_type(SemanticAnalyzer* analyzer) {
    // 这是一个简化实现
    // 实际实现中应该跟踪当前正在分析的函数
    return TYPE_UNKNOWN;
}

/* 运行语义分析 */
ErrorList* semantic_analyze(AST* ast) {
    if (!ast) {
        ErrorList* errors = error_list_create();
        error_list_add(errors, "无法分析空的语法树");
        return errors;
    }
    
    SemanticAnalyzer* analyzer = semantic_analyzer_create(ast);
    if (!analyzer) {
        ErrorList* errors = error_list_create();
        error_list_add(errors, "无法创建语义分析器");
        return errors;
    }
    
    // 分析程序的每个顶级语句
    for (int i = 0; i < ast->root_node_count; i++) {
        analyze_statement(analyzer, ast->root_nodes[i]);
    }
    
    // 克隆错误列表以便返回
    ErrorList* errors = error_list_clone(analyzer->errors);
    
    // 释放分析器
    semantic_analyzer_destroy(analyzer);
    
    return errors;
} 