// QEntL最小化运行时 - 主程序
// 提供命令行接口和测试功能

#include "runtime.h"
#include "bytecode.h"
#include <stdio.h>
#include <string.h>
#include <stdlib.h>

// ==================== 命令行帮助 ====================

void print_help(void) {
    printf("QEntL最小化C运行时 - 版本 0.1.0\n");
    printf("为QEntL量子语言提供最小化运行时支持\n");
    printf("\n");
    printf("用法: qentl_runtime [选项] [文件]\n");
    printf("\n");
    printf("选项:\n");
    printf("  --help, -h        显示此帮助信息\n");
    printf("  --version, -v     显示版本信息\n");
    printf("  --test, -t        运行内置测试\n");
    printf("  --disassemble, -d 反汇编字节码文件\n");
    printf("  --memory-stats    显示内存统计信息\n");
    printf("  --run-compiler    运行QEntL编译器测试\n");
    printf("\n");
    printf("文件:\n");
    printf("  如果没有指定选项，尝试执行指定的字节码文件\n");
    printf("\n");
    printf("示例:\n");
    printf("  qentl_runtime --test\n");
    printf("  qentl_runtime program.qbc\n");
    printf("  qentl_runtime -d program.qbc\n");
}

void print_version(void) {
    printf("QEntL最小化C运行时 版本 0.1.0\n");
    printf("量子基因编码: QGC-RUNTIME-20260203\n");
    printf("编译时间: %s %s\n", __DATE__, __TIME__);
    printf("架构: %s\n", 
#ifdef __x86_64__
           "x86_64"
#elif defined(__i386__)
           "i386"
#elif defined(__aarch64__)
           "ARM64"
#else
           "未知"
#endif
    );
}

// ==================== 文件加载 ====================

uint8_t* load_file(const char* filename, size_t* out_size) {
    FILE* file = fopen(filename, "rb");
    if (file == NULL) {
        fprintf(stderr, "无法打开文件: %s\n", filename);
        return NULL;
    }
    
    // 获取文件大小
    fseek(file, 0, SEEK_END);
    long file_size = ftell(file);
    fseek(file, 0, SEEK_SET);
    
    if (file_size <= 0) {
        fprintf(stderr, "文件为空或无效: %s\n", filename);
        fclose(file);
        return NULL;
    }
    
    // 分配内存
    uint8_t* buffer = (uint8_t*)runtime_alloc(file_size);
    if (buffer == NULL) {
        fprintf(stderr, "内存分配失败: %ld 字节\n", file_size);
        fclose(file);
        return NULL;
    }
    
    // 读取文件
    size_t bytes_read = fread(buffer, 1, file_size, file);
    if (bytes_read != (size_t)file_size) {
        fprintf(stderr, "读取文件失败: 期望 %ld 字节，实际 %zu 字节\n", 
                file_size, bytes_read);
        runtime_free(buffer);
        fclose(file);
        return NULL;
    }
    
    fclose(file);
    
    *out_size = bytes_read;
    return buffer;
}

// ==================== 命令处理 ====================

int handle_test_command(void) {
    printf("运行QEntL运行时测试...\n");
    
    // 运行虚拟机测试
    vm_run_test();
    
    // 运行内存测试
    runtime_print_memory_stats();
    
    return 0;
}

int handle_disassemble_command(const char* filename) {
    printf("反汇编文件: %s\n", filename);
    
    size_t file_size;
    uint8_t* code = load_file(filename, &file_size);
    if (code == NULL) {
        return 1;
    }
    
    bytecode_disassemble(code, file_size);
    
    runtime_free(code);
    return 0;
}

int handle_run_command(const char* filename) {
    printf("执行字节码文件: %s\n", filename);
    
    size_t file_size;
    uint8_t* code = load_file(filename, &file_size);
    if (code == NULL) {
        return 1;
    }
    
    // 创建虚拟机并执行
    VM* vm = vm_create();
    if (vm == NULL) {
        fprintf(stderr, "创建虚拟机失败\n");
        runtime_free(code);
        return 1;
    }
    
    vm_load_bytecode(vm, code, file_size);
    
    printf("开始执行...\n");
    int result = vm_execute(vm);
    printf("执行完成，退出代码: %d\n", result);
    
    vm_free(vm);
    runtime_free(code);
    
    return result;
}

int handle_run_compiler_test(void) {
    printf("运行QEntL编译器测试...\n");
    
    // 调用真正的QEntL编译器演示
    return runtime_execute_qentl_compiler(NULL);
}

// ==================== 主函数 ====================

int main(int argc, char* argv[]) {
    printf("⚛️ QEntL最小化C运行时启动\n");
    printf("服务人类三大圣律贯穿始终\n");
    printf("为每个人服务，服务人类！\n\n");
    
    // 如果没有参数，显示帮助
    if (argc == 1) {
        print_help();
        return 0;
    }
    
    // 处理命令行参数
    for (int i = 1; i < argc; i++) {
        const char* arg = argv[i];
        
        if (strcmp(arg, "--help") == 0 || strcmp(arg, "-h") == 0) {
            print_help();
            return 0;
            
        } else if (strcmp(arg, "--version") == 0 || strcmp(arg, "-v") == 0) {
            print_version();
            return 0;
            
        } else if (strcmp(arg, "--test") == 0 || strcmp(arg, "-t") == 0) {
            return handle_test_command();
            
        } else if (strcmp(arg, "--disassemble") == 0 || strcmp(arg, "-d") == 0) {
            if (i + 1 >= argc) {
                fprintf(stderr, "错误: --disassemble 需要文件名参数\n");
                return 1;
            }
            return handle_disassemble_command(argv[++i]);
            
        } else if (strcmp(arg, "--memory-stats") == 0) {
            runtime_print_memory_stats();
            return 0;
            
        } else if (strcmp(arg, "--run-compiler") == 0) {
            return handle_run_compiler_test();
            
        } else if (arg[0] == '-') {
            fprintf(stderr, "未知选项: %s\n", arg);
            fprintf(stderr, "使用 --help 查看可用选项\n");
            return 1;
            
        } else {
            // 假设是文件名，尝试执行
            return handle_run_command(arg);
        }
    }
    
    return 0;
}