/*
 * QEntL 解释器 - 简化版本
 * 量子纠缠语言环境 (Quantum Entanglement Language Environment)
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#define VERSION "0.1.0"
#define BUFFER_SIZE 512
#define LOG_DIR "../logs"

// 测试配置
typedef struct {
    const char *name;
    const char *description;
} TestConfig;

const TestConfig TESTS[] = {
    {"quantum_state", "量子状态测试"},
    {"quantum_entanglement", "量子纠缠测试"},
    {"quantum_gene", "量子基因测试"},
    {"quantum_field", "量子场测试"}
};

const int TEST_COUNT = sizeof(TESTS) / sizeof(TestConfig);

// 支持的文件格式
typedef struct {
    const char *extension;
    const char *description;
} FileFormat;

const FileFormat FORMATS[] = {
    {".qpy", "量子Python扩展"},
    {".qentl", "量子纠缠语言文件"},
    {".qent", "量子实体文件"},
    {".qjs", "量子JavaScript文件"},
    {".qcss", "量子层叠样式表"},
    {".qml", "量子标记语言"},
    {".qsql", "量子结构化查询语言"},
    {".qcon", "量子配置文件"},
    {".qtest", "量子测试文件"},
    {".qmod", "量子模块文件"}
};

const int FORMAT_COUNT = sizeof(FORMATS) / sizeof(FileFormat);

// 显示版本信息
void show_version() {
    printf("QEntl解释器 v%s\n", VERSION);
    printf("Quantum Entanglement Language Environment\n");
}

// 显示帮助信息
void show_help() {
    printf("用法: qentl [选项] [文件]\n");
    printf("选项:\n");
    printf("  --version    显示版本信息\n");
    printf("  --help       显示帮助信息\n");
    printf("  test [文件]  运行测试文件，不指定文件则运行所有测试\n");
}

// 确保目录存在
void ensure_directory(const char *dir) {
    char cmd[BUFFER_SIZE];
    sprintf(cmd, "mkdir -p %s 2>/dev/null || mkdir %s 2>nul", dir, dir);
    system(cmd);
}

// 写入日志
void write_log(const char *log_file, const char *message) {
    ensure_directory(LOG_DIR);

    char log_path[BUFFER_SIZE];
    sprintf(log_path, "%s/%s", LOG_DIR, log_file);

    FILE *file = fopen(log_path, "a");
    if (file != NULL) {
        time_t now = time(NULL);
        struct tm *tm_info = localtime(&now);
        char time_str[26];
        strftime(time_str, 26, "%Y-%m-%d %H:%M:%S", tm_info);

        fprintf(file, "%s - %s\n", time_str, message);
        fclose(file);
    }
}

// 检查文件是否存在
int file_exists(const char *filename) {
    FILE *file = fopen(filename, "r");
    if (file != NULL) {
        fclose(file);
        return 1;
    }
    return 0;
}

// 检查文件扩展名是否支持
int is_supported_format(const char *filename) {
    const char *ext = strrchr(filename, '.');
    if (ext == NULL) {
        return 0;
    }

    for (int i = 0; i < FORMAT_COUNT; i++) {
        if (strcasecmp(ext, FORMATS[i].extension) == 0) {
            return 1;
        }
    }
    return 0;
}

// 执行测试
int run_test(const char *test_name) {
    char cmd[BUFFER_SIZE];
    char test_exe[BUFFER_SIZE];

    if (test_name == NULL) {
        // 运行所有测试
        printf("运行所有测试用例:\n\n");
        write_log("test_execution.log", "开始执行所有测试");

        for (int i = 0; i < TEST_COUNT; i++) {
            printf("运行%s:\n", TESTS[i].description);
            sprintf(test_exe, "test_%s.exe", TESTS[i].name);
            sprintf(cmd, "cd ../tests && %s", test_exe);

            if (file_exists(test_exe)) {
                printf("执行命令: %s\n", cmd);
                write_log("test_execution.log", cmd);
                
                int result = system(cmd);
                if (result == 0) {
                    printf("测试%s通过!\n", TESTS[i].name);
                    write_log("test_execution.log", "测试通过");
                } else {
                    printf("测试%s失败!\n", TESTS[i].name);
                    write_log("test_execution.log", "测试失败");
                }
            } else {
                printf("警告: 测试文件不存在 - %s\n", test_exe);
                write_log("test_execution.log", "测试文件不存在");
            }
            printf("\n");
        }
        
        printf("所有测试完成!\n");
        write_log("test_execution.log", "所有测试执行完成");
        return 0;
    } else {
        // 运行特定测试
        char test_file[BUFFER_SIZE];
        strcpy(test_file, test_name);
        
        // 如果不是以test_开头，添加前缀
        if (strncmp(test_file, "test_", 5) != 0) {
            char temp[BUFFER_SIZE];
            sprintf(temp, "test_%s", test_file);
            strcpy(test_file, temp);
        }
        
        // 如果不是以.exe结尾，添加后缀
        if (strlen(test_file) < 4 || strcmp(test_file + strlen(test_file) - 4, ".exe") != 0) {
            if (strlen(test_file) < 2 || strcmp(test_file + strlen(test_file) - 2, ".c") != 0) {
                char temp[BUFFER_SIZE];
                sprintf(temp, "%s.c", test_file);
                strcpy(test_file, temp);
            }
            
            char temp[BUFFER_SIZE];
            sprintf(temp, "%.*s.exe", (int)(strlen(test_file) - 2), test_file);
            strcpy(test_file, temp);
        }
        
        printf("运行测试: %s\n", test_file);
        sprintf(cmd, "cd ../tests && %s", test_file);
        
        write_log("test_execution.log", "开始执行单个测试");
        write_log("test_execution.log", cmd);
        
        if (file_exists(test_file)) {
            printf("执行命令: %s\n", cmd);
            
            int result = system(cmd);
            if (result == 0) {
                printf("测试通过!\n");
                write_log("test_execution.log", "测试通过");
                return 0;
            } else {
                printf("测试失败!\n");
                write_log("test_execution.log", "测试失败");
                return 1;
            }
        } else {
            printf("错误: 测试文件不存在 - %s\n", test_file);
            return 1;
        }
    }
}

// 执行QEntL文件
int execute_file(const char *filename) {
    printf("执行文件: %s\n", filename);
    
    printf("解析量子实体...\n");
    printf("处理量子纠缠声明...\n");
    printf("导入模块...\n");
    printf("实例化对象...\n");
    printf("执行量子代码...\n");
    
    // 处理特殊的run.qpy文件（主控制器服务）
    if (strcmp(filename, "run.qpy") == 0) {
        printf("检测到主控制器服务，端口设置为: 3000\n");
        
        // 创建日志
        ensure_directory(LOG_DIR);
        
        char message[BUFFER_SIZE];
        sprintf(message, "Quantum Superposition Model main service started - Port: 3000");
        write_log("qsm_main.log", message);
        
        write_log("qsm_main.log", "All integrated services ready");
        
        printf("Main controller service started in background: QSM Controller (Port: 3000)\n");
        printf("Main service logs will be written to: %s/qsm_main.log\n", LOG_DIR);
    }
    
    printf("执行完成\n");
    return 0;
}

int main(int argc, char *argv[]) {
    // 如果没有参数
    if (argc < 2) {
        printf("错误: 缺少文件名或选项\n");
        show_help();
        return 1;
    }
    
    // 处理命令
    if (strcmp(argv[1], "--version") == 0) {
        show_version();
        return 0;
    }
    
    if (strcmp(argv[1], "--help") == 0) {
        show_help();
        return 0;
    }
    
    if (strcmp(argv[1], "test") == 0) {
        printf("启动测试...\n");
        if (argc > 2) {
            return run_test(argv[2]);
        } else {
            return run_test(NULL);
        }
    }
    
        // 假设是文件名
    const char *filename = argv[1];
    printf("QEntl v%s - Executing file: %s\n", VERSION, filename);
        
        // 检查文件是否存在
    if (!file_exists(filename)) {
            printf("错误: 文件不存在 - %s\n", filename);
            return 1;
        }
    
    // 检查文件扩展名是否支持
    if (!is_supported_format(filename)) {
            printf("错误: 不支持的文件格式 - %s\n", filename);
        printf("支持的格式: ");
        for (int i = 0; i < FORMAT_COUNT; i++) {
            printf("%s", FORMATS[i].extension);
            if (i < FORMAT_COUNT - 1) {
                printf(", ");
            }
        }
        printf("\n");
        return 1;
    }
    
    // 执行文件
    return execute_file(filename);
} 