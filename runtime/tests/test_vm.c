// QEntL虚拟机测试程序
// 版本: 1.0.0

#include "../include/qentl_runtime.h"
#include "../include/qentl_vm.h"
#include <stdio.h>

void test_basic_vm(void) {
    printf("=== 测试基础虚拟机功能 ===\n");
    
    // 创建虚拟机
    QentlVM* vm = qentl_vm_create();
    if (vm == NULL) {
        printf("❌ 创建虚拟机失败\n");
        return;
    }
    printf("✅ 虚拟机创建成功\n");
    
    // 创建字节码块
    BytecodeChunk* chunk = qentl_bytecode_create();
    if (chunk == NULL) {
        printf("❌ 创建字节码块失败\n");
        qentl_vm_destroy(vm);
        return;
    }
    printf("✅ 字节码块创建成功\n");
    
    // 准备常量：数字7
    vm->constants[0] = qentl_value_integer(7);
    vm->constants_count = 1;
    
    // 添加指令：加载常量0 -> 打印 -> 停止
    size_t instr1 = qentl_bytecode_add_instruction(chunk, OP_LOAD_CONST, 0);
    size_t instr2 = qentl_bytecode_add_instruction(chunk, OP_PRINT, 0);
    size_t instr3 = qentl_bytecode_add_instruction(chunk, OP_HALT, 0);
    
    if (instr1 == (size_t)-1 || instr2 == (size_t)-1 || instr3 == (size_t)-1) {
        printf("❌ 添加指令失败\n");
        qentl_bytecode_destroy(chunk);
        qentl_vm_destroy(vm);
        return;
    }
    printf("✅ 指令添加成功 (LOAD_CONST, PRINT, HALT)\n");
    
    // 反汇编字节码
    printf("\n字节码反汇编:\n");
    qentl_bytecode_disassemble(chunk, "测试程序");
    
    // 加载并执行
    if (!qentl_vm_load_chunk(vm, chunk)) {
        printf("❌ 加载字节码块失败\n");
        qentl_bytecode_destroy(chunk);
        qentl_vm_destroy(vm);
        return;
    }
    printf("✅ 字节码块加载成功\n");
    
    printf("\n执行输出:\n");
    if (!qentl_vm_execute(vm)) {
        printf("❌ 虚拟机执行失败\n");
    } else {
        printf("✅ 虚拟机执行成功\n");
    }
    
    // 清理
    qentl_bytecode_destroy(chunk);
    qentl_vm_destroy(vm);
    printf("✅ 资源清理完成\n");
}

void test_arithmetic_vm(void) {
    printf("\n=== 测试算术运算 ===\n");
    
    QentlVM* vm = qentl_vm_create();
    BytecodeChunk* chunk = qentl_bytecode_create();
    
    if (!vm || !chunk) {
        printf("❌ 初始化失败\n");
        if (vm) qentl_vm_destroy(vm);
        if (chunk) qentl_bytecode_destroy(chunk);
        return;
    }
    
    // 设置常量：3 和 4
    vm->constants[0] = qentl_value_integer(3);
    vm->constants[1] = qentl_value_integer(4);
    vm->constants_count = 2;
    
    // 程序：3 + 4
    qentl_bytecode_add_instruction(chunk, OP_LOAD_CONST, 0);  // 加载3
    qentl_bytecode_add_instruction(chunk, OP_LOAD_CONST, 1);  // 加载4
    qentl_bytecode_add_instruction(chunk, OP_ADD, 0);         // 相加
    qentl_bytecode_add_instruction(chunk, OP_PRINT, 0);       // 打印结果
    qentl_bytecode_add_instruction(chunk, OP_HALT, 0);        // 停止
    
    qentl_vm_load_chunk(vm, chunk);
    
    printf("计算 3 + 4 = ");
    if (!qentl_vm_execute(vm)) {
        printf("❌ 计算失败\n");
    }
    
    qentl_bytecode_destroy(chunk);
    qentl_vm_destroy(vm);
}

void test_global_variables(void) {
    printf("\n=== 测试全局变量 ===\n");
    
    QentlVM* vm = qentl_vm_create();
    BytecodeChunk* chunk = qentl_bytecode_create();
    
    if (!vm || !chunk) {
        printf("❌ 初始化失败\n");
        return;
    }
    
    // 设置常量：42
    vm->constants[0] = qentl_value_integer(42);
    vm->constants_count = 1;
    
    // 程序：设置全局变量，然后读取并打印
    qentl_bytecode_add_instruction(chunk, OP_LOAD_CONST, 0);  // 加载42
    qentl_bytecode_add_instruction(chunk, OP_STORE_GLOBAL, 0); // 存储到全局0
    qentl_bytecode_add_instruction(chunk, OP_LOAD_GLOBAL, 0);  // 从全局0加载
    qentl_bytecode_add_instruction(chunk, OP_PRINT, 0);       // 打印
    qentl_bytecode_add_instruction(chunk, OP_HALT, 0);        // 停止
    
    qentl_vm_load_chunk(vm, chunk);
    
    printf("全局变量测试: ");
    if (!qentl_vm_execute(vm)) {
        printf("❌ 测试失败\n");
    }
    
    qentl_bytecode_destroy(chunk);
    qentl_vm_destroy(vm);
}

int main(void) {
    printf("QEntL虚拟机测试套件\n");
    printf("==================\n\n");
    
    // 初始化日志系统
    qentl_log_init(QENTL_LOG_INFO, true);
    
    // 运行测试
    test_basic_vm();
    test_arithmetic_vm();
    test_global_variables();
    
    printf("\n=== 所有测试完成 ===\n");
    return 0;
}