/**
 * @file main.c
 * @brief 量子性能分析器命令行界面
 * @author QEntL开发团队
 * @version 1.0
 * @date 2024-06-10
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include "profiler_core.h"

void print_usage(const char* program_name) {
    printf("量子性能分析器使用方法:\n");
    printf("%s [选项] <命令> [参数]\n\n", program_name);
    
    printf("可用命令:\n");
    printf("  test               运行内置测试\n");
    printf("  profile <程序>     分析指定程序的性能\n");
    printf("  compare <文件1> <文件2> <输出文件>  比较两个性能报告\n");
    printf("  report <文件>      显示一个性能报告的摘要\n");
    printf("\n");
    
    printf("选项:\n");
    printf("  -l, --level <级别>  指定分析级别 (basic, standard, detailed, quantum)\n");
    printf("  -o, --output <文件>  输出报告文件\n");
    printf("  -h, --help           显示此帮助信息\n");
    printf("\n");
    
    printf("示例:\n");
    printf("  %s --level quantum test\n", program_name);
    printf("  %s -l detailed -o report.txt profile ./my_quantum_program\n", program_name);
    printf("  %s compare report1.txt report2.txt diff.txt\n", program_name);
}

ProfileLevel parse_level_str(const char* level_str) {
    if (!level_str) return PROFILE_LEVEL_STANDARD;
    
    if (strcmp(level_str, "basic") == 0) {
        return PROFILE_LEVEL_BASIC;
    } else if (strcmp(level_str, "standard") == 0) {
        return PROFILE_LEVEL_STANDARD;
    } else if (strcmp(level_str, "detailed") == 0) {
        return PROFILE_LEVEL_DETAILED;
    } else if (strcmp(level_str, "quantum") == 0) {
        return PROFILE_LEVEL_QUANTUM;
    }
    
    printf("警告: 未知分析级别 '%s'，使用标准级别\n", level_str);
    return PROFILE_LEVEL_STANDARD;
}

int run_profiler_test(ProfileLevel level, const char* output_file) {
    // 创建分析器
    QuantumProfiler* profiler = quantum_profiler_create(level);
    if (!profiler) {
        fprintf(stderr, "错误: 无法创建性能分析器\n");
        return 1;
    }
    
    // 运行测试
    bool test_result = quantum_profiler_run_test();
    
    // 生成报告（如果指定）
    if (output_file) {
        quantum_profiler_generate_report(profiler, output_file);
    }
    
    // 打印摘要
    quantum_profiler_print_summary(profiler);
    
    // 销毁分析器
    quantum_profiler_destroy(profiler);
    
    return test_result ? 0 : 1;
}

int run_profiler_profile(const char* target_program, ProfileLevel level, const char* output_file) {
    printf("分析功能尚未实现\n");
    printf("目标程序: %s\n", target_program);
    printf("分析级别: %d\n", level);
    if (output_file) {
        printf("输出文件: %s\n", output_file);
    }
    
    // 这里应该实现调用目标程序并附加分析器的逻辑
    // 由于这需要深度集成到运行时，目前仅是占位符
    
    return 0;
}

int run_profiler_compare(const char* file1, const char* file2, const char* output_file) {
    printf("比较功能尚未实现\n");
    printf("文件1: %s\n", file1);
    printf("文件2: %s\n", file2);
    printf("输出文件: %s\n", output_file);
    
    // 应该实现两个报告文件的读取和比较功能
    
    return 0;
}

int run_profiler_report(const char* report_file) {
    printf("报告查看功能尚未实现\n");
    printf("报告文件: %s\n", report_file);
    
    // 应该实现报告文件的解析和显示功能
    
    return 0;
}

int main(int argc, char* argv[]) {
    // 默认值
    ProfileLevel level = PROFILE_LEVEL_STANDARD;
    const char* output_file = NULL;
    const char* command = NULL;
    
    // 解析命令行参数
    for (int i = 1; i < argc; i++) {
        if (strcmp(argv[i], "-h") == 0 || strcmp(argv[i], "--help") == 0) {
            print_usage(argv[0]);
            return 0;
        } else if (strcmp(argv[i], "-l") == 0 || strcmp(argv[i], "--level") == 0) {
            if (i + 1 < argc) {
                level = parse_level_str(argv[++i]);
            } else {
                fprintf(stderr, "错误: --level 选项需要一个参数\n");
                return 1;
            }
        } else if (strcmp(argv[i], "-o") == 0 || strcmp(argv[i], "--output") == 0) {
            if (i + 1 < argc) {
                output_file = argv[++i];
            } else {
                fprintf(stderr, "错误: --output 选项需要一个参数\n");
                return 1;
            }
        } else if (!command) {
            command = argv[i];
        } else {
            // 剩余参数将在各命令处理函数中解析
            break;
        }
    }
    
    // 检查是否指定了命令
    if (!command) {
        fprintf(stderr, "错误: 未指定命令\n");
        print_usage(argv[0]);
        return 1;
    }
    
    // 执行相应的命令
    if (strcmp(command, "test") == 0) {
        return run_profiler_test(level, output_file);
    } else if (strcmp(command, "profile") == 0) {
        if (argc < 3) {
            fprintf(stderr, "错误: profile 命令需要指定目标程序\n");
            return 1;
        }
        return run_profiler_profile(argv[argc - 1], level, output_file);
    } else if (strcmp(command, "compare") == 0) {
        if (argc < 5) {
            fprintf(stderr, "错误: compare 命令需要两个输入文件和一个输出文件\n");
            return 1;
        }
        return run_profiler_compare(argv[argc - 3], argv[argc - 2], argv[argc - 1]);
    } else if (strcmp(command, "report") == 0) {
        if (argc < 3) {
            fprintf(stderr, "错误: report 命令需要指定报告文件\n");
            return 1;
        }
        return run_profiler_report(argv[argc - 1]);
    } else {
        fprintf(stderr, "错误: 未知命令 '%s'\n", command);
        print_usage(argv[0]);
        return 1;
    }
    
    return 0;
} 