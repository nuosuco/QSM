/**
 * QEntL量子状态可视化工具主程序
 * 作者：QEntL开发团队
 * 版本：1.0
 * 日期：2024年5月19日
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <complex.h>
#include <stdbool.h>
#include <math.h>
#include <time.h>
#include <getopt.h>
#include "visualizer_core.h"

#define VERSION "1.0"
#define MAX_QUBITS 16

// 命令行选项
struct {
    char* input_file;
    char* output_file;
    bool show_help;
    bool show_version;
    bool interactive;
    bool console_mode;
    ColorScheme color_scheme;
    bool no_bloch;
    bool no_phase;
    bool no_probabilities;
    bool no_animation;
    VectorRepresentation vector_representation;
    int example_qubits;
} options = {
    .input_file = NULL,
    .output_file = NULL,
    .show_help = false,
    .show_version = false,
    .interactive = false,
    .console_mode = true,
    .color_scheme = SCHEME_DEFAULT,
    .no_bloch = false,
    .no_phase = false,
    .no_probabilities = false,
    .no_animation = false,
    .vector_representation = VECTOR_ARROWS,
    .example_qubits = 0
};

// 显示帮助信息
void show_help(void) {
    printf("QEntL量子状态可视化工具 v%s\n", VERSION);
    printf("用法: qentl_visualizer [选项] [量子态文件]\n");
    printf("\n");
    printf("选项:\n");
    printf("  -h, --help             显示帮助信息\n");
    printf("  -v, --version          显示版本信息\n");
    printf("  -o, --output=FILE      输出到文件\n");
    printf("  -i, --interactive      交互式模式\n");
    printf("  -c, --color=SCHEME     设置颜色方案 (default, dark, light, vibrant, pastel)\n");
    printf("  -r, --representation=TYPE 设置向量表示方式 (arrows, bars, circles, spheres)\n");
    printf("  --no-bloch             不显示布洛赫球\n");
    printf("  --no-phase             不显示相位信息\n");
    printf("  --no-probabilities     不显示概率分布\n");
    printf("  --no-animation         不启用动画\n");
    printf("  -e, --example=QUBITS   创建示例量子态 (1-16量子比特)\n");
    printf("\n");
    printf("示例:\n");
    printf("  qentl_visualizer bell_state.qstate\n");
    printf("  qentl_visualizer --example=2 --color=vibrant\n");
    printf("  qentl_visualizer -i -o result.txt\n");
}

// 显示版本信息
void show_version(void) {
    printf("QEntL量子状态可视化工具 v%s\n", VERSION);
    printf("版权所有 (C) 2024 QEntL开发团队\n");
}

// 解析命令行参数
void parse_arguments(int argc, char** argv) {
    static struct option long_options[] = {
        {"help",            no_argument,       0, 'h'},
        {"version",         no_argument,       0, 'v'},
        {"output",          required_argument, 0, 'o'},
        {"interactive",     no_argument,       0, 'i'},
        {"color",           required_argument, 0, 'c'},
        {"representation",  required_argument, 0, 'r'},
        {"no-bloch",        no_argument,       0, 1000},
        {"no-phase",        no_argument,       0, 1001},
        {"no-probabilities",no_argument,       0, 1002},
        {"no-animation",    no_argument,       0, 1003},
        {"example",         required_argument, 0, 'e'},
        {0, 0, 0, 0}
    };
    
    int opt;
    int option_index = 0;
    
    while ((opt = getopt_long(argc, argv, "hvo:ic:r:e:", long_options, &option_index)) != -1) {
        switch (opt) {
            case 'h':
                options.show_help = true;
                break;
                
            case 'v':
                options.show_version = true;
                break;
                
            case 'o':
                options.output_file = optarg;
                options.console_mode = false;
                break;
                
            case 'i':
                options.interactive = true;
                break;
                
            case 'c':
                if (strcmp(optarg, "dark") == 0) {
                    options.color_scheme = SCHEME_DARK;
                } else if (strcmp(optarg, "light") == 0) {
                    options.color_scheme = SCHEME_LIGHT;
                } else if (strcmp(optarg, "vibrant") == 0) {
                    options.color_scheme = SCHEME_VIBRANT;
                } else if (strcmp(optarg, "pastel") == 0) {
                    options.color_scheme = SCHEME_PASTEL;
                } else {
                    options.color_scheme = SCHEME_DEFAULT;
                }
                break;
                
            case 'r':
                if (strcmp(optarg, "bars") == 0) {
                    options.vector_representation = VECTOR_BARS;
                } else if (strcmp(optarg, "circles") == 0) {
                    options.vector_representation = VECTOR_CIRCLES;
                } else if (strcmp(optarg, "spheres") == 0) {
                    options.vector_representation = VECTOR_SPHERES;
                } else {
                    options.vector_representation = VECTOR_ARROWS;
                }
                break;
                
            case 'e':
                options.example_qubits = atoi(optarg);
                if (options.example_qubits < 1) options.example_qubits = 1;
                if (options.example_qubits > MAX_QUBITS) options.example_qubits = MAX_QUBITS;
                break;
                
            case 1000:
                options.no_bloch = true;
                break;
                
            case 1001:
                options.no_phase = true;
                break;
                
            case 1002:
                options.no_probabilities = true;
                break;
                
            case 1003:
                options.no_animation = true;
                break;
                
            default:
                // 未知选项
                break;
        }
    }
    
    // 获取输入文件名
    if (optind < argc) {
        options.input_file = argv[optind];
    }
}

// 创建示例量子态
complex double* create_example_state(int qubit_count) {
    if (qubit_count <= 0 || qubit_count > MAX_QUBITS) return NULL;
    
    int state_count = 1 << qubit_count;
    complex double* amplitudes = (complex double*)calloc(state_count, sizeof(complex double));
    if (!amplitudes) return NULL;
    
    srand(time(NULL));
    
    // 根据量子比特数量创建不同类型的示例态
    if (qubit_count == 1) {
        // 创建随机单量子比特态
        double theta = ((double)rand() / RAND_MAX) * M_PI;
        double phi = ((double)rand() / RAND_MAX) * 2.0 * M_PI;
        
        amplitudes[0] = cos(theta / 2.0);
        amplitudes[1] = sin(theta / 2.0) * cexp(I * phi);
    } else if (qubit_count == 2) {
        // 创建贝尔态之一
        int bell_type = rand() % 4;
        switch (bell_type) {
            case 0: // |Φ+⟩ = (|00⟩ + |11⟩)/√2
                amplitudes[0] = 1.0 / sqrt(2.0);
                amplitudes[3] = 1.0 / sqrt(2.0);
                break;
            case 1: // |Φ-⟩ = (|00⟩ - |11⟩)/√2
                amplitudes[0] = 1.0 / sqrt(2.0);
                amplitudes[3] = -1.0 / sqrt(2.0);
                break;
            case 2: // |Ψ+⟩ = (|01⟩ + |10⟩)/√2
                amplitudes[1] = 1.0 / sqrt(2.0);
                amplitudes[2] = 1.0 / sqrt(2.0);
                break;
            case 3: // |Ψ-⟩ = (|01⟩ - |10⟩)/√2
                amplitudes[1] = 1.0 / sqrt(2.0);
                amplitudes[2] = -1.0 / sqrt(2.0);
                break;
        }
    } else if (qubit_count == 3) {
        // 创建GHZ态 (|000⟩ + |111⟩)/√2
        amplitudes[0] = 1.0 / sqrt(2.0);
        amplitudes[7] = 1.0 / sqrt(2.0);
    } else {
        // 创建一个随机态
        double sum = 0.0;
        
        // 生成随机振幅
        for (int i = 0; i < state_count; i++) {
            double real = ((double)rand() / RAND_MAX) * 2.0 - 1.0;
            double imag = ((double)rand() / RAND_MAX) * 2.0 - 1.0;
            amplitudes[i] = real + I * imag;
            sum += cabs(amplitudes[i]) * cabs(amplitudes[i]);
        }
        
        // 归一化
        double norm = sqrt(sum);
        for (int i = 0; i < state_count; i++) {
            amplitudes[i] /= norm;
        }
    }
    
    return amplitudes;
}

// 创建示例纠缠矩阵
double** create_example_entanglement_matrix(int qubit_count) {
    if (qubit_count <= 0 || qubit_count > MAX_QUBITS) return NULL;
    
    double** matrix = (double**)malloc(qubit_count * sizeof(double*));
    if (!matrix) return NULL;
    
    for (int i = 0; i < qubit_count; i++) {
        matrix[i] = (double*)calloc(qubit_count, sizeof(double));
        if (!matrix[i]) {
            for (int j = 0; j < i; j++) {
                free(matrix[j]);
            }
            free(matrix);
            return NULL;
        }
    }
    
    // 设置纠缠值
    srand(time(NULL) + 1000);
    for (int i = 0; i < qubit_count; i++) {
        for (int j = i + 1; j < qubit_count; j++) {
            double value = ((double)rand() / RAND_MAX);
            matrix[i][j] = value;
            matrix[j][i] = value;
        }
    }
    
    return matrix;
}

// 从文件加载量子态
complex double* load_quantum_state_from_file(const char* filename, int* qubit_count) {
    if (!filename || !qubit_count) return NULL;
    
    FILE* file = fopen(filename, "rb");
    if (!file) {
        fprintf(stderr, "错误：无法打开文件 %s\n", filename);
        return NULL;
    }
    
    // 读取量子比特数量
    if (fread(qubit_count, sizeof(int), 1, file) != 1) {
        fprintf(stderr, "错误：无法读取量子比特数量\n");
        fclose(file);
        return NULL;
    }
    
    if (*qubit_count <= 0 || *qubit_count > MAX_QUBITS) {
        fprintf(stderr, "错误：无效的量子比特数量 %d\n", *qubit_count);
        fclose(file);
        return NULL;
    }
    
    int state_count = 1 << *qubit_count;
    complex double* amplitudes = (complex double*)malloc(state_count * sizeof(complex double));
    if (!amplitudes) {
        fprintf(stderr, "错误：无法分配内存\n");
        fclose(file);
        return NULL;
    }
    
    // 读取状态振幅
    if (fread(amplitudes, sizeof(complex double), state_count, file) != state_count) {
        fprintf(stderr, "错误：无法读取状态振幅\n");
        free(amplitudes);
        fclose(file);
        return NULL;
    }
    
    fclose(file);
    return amplitudes;
}

// 交互式模式
void run_interactive_mode(Visualizer* vis) {
    printf("QEntL量子状态可视化工具 - 交互式模式\n");
    printf("输入 'help' 查看可用命令\n");
    
    char command[256];
    bool running = true;
    
    while (running) {
        printf("> ");
        if (fgets(command, sizeof(command), stdin) == NULL) break;
        
        // 移除换行符
        size_t len = strlen(command);
        if (len > 0 && command[len-1] == '\n') {
            command[len-1] = '\0';
        }
        
        // 处理命令
        if (strcmp(command, "exit") == 0 || strcmp(command, "quit") == 0) {
            running = false;
        } else if (strcmp(command, "help") == 0) {
            printf("可用命令:\n");
            printf("  help                - 显示此帮助信息\n");
            printf("  exit, quit          - 退出程序\n");
            printf("  show                - 显示当前量子态\n");
            printf("  load <filename>     - 从文件加载量子态\n");
            printf("  save <filename>     - 保存可视化结果到文件\n");
            printf("  example <qubits>    - 创建示例量子态\n");
            printf("  measure <times>     - 对当前态进行多次测量\n");
            printf("  config              - 显示当前配置\n");
            printf("  set <option> <value>- 设置配置选项\n");
        } else if (strcmp(command, "show") == 0) {
            visualizer_visualize(vis);
        } else if (strncmp(command, "load ", 5) == 0) {
            char* filename = command + 5;
            while (isspace(*filename)) filename++;
            
            int qubit_count;
            complex double* amplitudes = load_quantum_state_from_file(filename, &qubit_count);
            if (amplitudes) {
                visualizer_set_quantum_state(vis, qubit_count, amplitudes);
                printf("已加载量子态: %d 量子比特\n", qubit_count);
                free(amplitudes);
            }
        } else if (strncmp(command, "save ", 5) == 0) {
            char* filename = command + 5;
            while (isspace(*filename)) filename++;
            
            if (visualizer_set_output_mode(vis, OUTPUT_FILE, filename)) {
                visualizer_visualize(vis);
                printf("可视化结果已保存到 %s\n", filename);
                visualizer_set_output_mode(vis, OUTPUT_CONSOLE, NULL);
            }
        } else if (strncmp(command, "example ", 8) == 0) {
            int qubits = atoi(command + 8);
            if (qubits > 0 && qubits <= MAX_QUBITS) {
                complex double* amplitudes = create_example_state(qubits);
                if (amplitudes) {
                    visualizer_set_quantum_state(vis, qubits, amplitudes);
                    printf("已创建 %d 量子比特示例态\n", qubits);
                    
                    // 为多量子比特态创建纠缠矩阵
                    if (qubits > 1) {
                        double** matrix = create_example_entanglement_matrix(qubits);
                        if (matrix) {
                            visualizer_set_entanglement_matrix(vis, qubits, (const double**)matrix);
                            
                            // 释放矩阵
                            for (int i = 0; i < qubits; i++) {
                                free(matrix[i]);
                            }
                            free(matrix);
                        }
                    }
                    
                    free(amplitudes);
                    visualizer_visualize(vis);
                }
            } else {
                printf("错误：量子比特数必须在 1 到 %d 之间\n", MAX_QUBITS);
            }
        } else if (strncmp(command, "measure ", 8) == 0) {
            int times = atoi(command + 8);
            if (times > 0) {
                // 模拟测量
                for (int i = 0; i < times; i++) {
                    double r = ((double)rand() / RAND_MAX);
                    double sum = 0.0;
                    int qubit_count, state_count;
                    VisualizerData data;
                    
                    // 获取当前态数据
                    visualizer_set_callback(vis, 
                        [](const VisualizerData* data, void* user_data) {
                            int* result = (int*)user_data;
                            *result = 0;
                            
                            if (!data || !data->amplitudes) return;
                            
                            double r = ((double)rand() / RAND_MAX);
                            double sum = 0.0;
                            int state_count = 1 << data->qubit_count;
                            
                            for (int i = 0; i < state_count; i++) {
                                double prob = cabs(data->amplitudes[i]) * cabs(data->amplitudes[i]);
                                sum += prob;
                                if (r <= sum) {
                                    *result = i;
                                    break;
                                }
                            }
                        }, 
                        &state
                    );
                    
                    int state = 0;
                    visualizer_visualize(vis);
                    visualizer_add_measurement(vis, state);
                }
                
                printf("已执行 %d 次测量\n", times);
                visualizer_visualize(vis);
            }
        } else if (strcmp(command, "config") == 0) {
            VisualizerConfig config;
            visualizer_get_config(vis, &config);
            
            printf("当前配置:\n");
            printf("  颜色方案: %d\n", config.color_scheme);
            printf("  布洛赫球: %s\n", config.bloch_sphere ? "开启" : "关闭");
            printf("  显示相位: %s\n", config.show_phase ? "开启" : "关闭");
            printf("  显示概率: %s\n", config.show_probabilities ? "开启" : "关闭");
            printf("  动画效果: %s\n", config.animation ? "开启" : "关闭");
            printf("  向量表示: %d\n", config.vector_representation);
        } else if (strncmp(command, "set ", 4) == 0) {
            char option[32], value[32];
            if (sscanf(command + 4, "%31s %31s", option, value) == 2) {
                VisualizerConfig config;
                visualizer_get_config(vis, &config);
                
                if (strcmp(option, "color") == 0) {
                    if (strcmp(value, "default") == 0) {
                        config.color_scheme = SCHEME_DEFAULT;
                    } else if (strcmp(value, "dark") == 0) {
                        config.color_scheme = SCHEME_DARK;
                    } else if (strcmp(value, "light") == 0) {
                        config.color_scheme = SCHEME_LIGHT;
                    } else if (strcmp(value, "vibrant") == 0) {
                        config.color_scheme = SCHEME_VIBRANT;
                    } else if (strcmp(value, "pastel") == 0) {
                        config.color_scheme = SCHEME_PASTEL;
                    }
                } else if (strcmp(option, "bloch") == 0) {
                    config.bloch_sphere = (strcmp(value, "on") == 0 || strcmp(value, "true") == 0);
                } else if (strcmp(option, "phase") == 0) {
                    config.show_phase = (strcmp(value, "on") == 0 || strcmp(value, "true") == 0);
                } else if (strcmp(option, "probabilities") == 0) {
                    config.show_probabilities = (strcmp(value, "on") == 0 || strcmp(value, "true") == 0);
                } else if (strcmp(option, "animation") == 0) {
                    config.animation = (strcmp(value, "on") == 0 || strcmp(value, "true") == 0);
                } else if (strcmp(option, "representation") == 0) {
                    if (strcmp(value, "arrows") == 0) {
                        config.vector_representation = VECTOR_ARROWS;
                    } else if (strcmp(value, "bars") == 0) {
                        config.vector_representation = VECTOR_BARS;
                    } else if (strcmp(value, "circles") == 0) {
                        config.vector_representation = VECTOR_CIRCLES;
                    } else if (strcmp(value, "spheres") == 0) {
                        config.vector_representation = VECTOR_SPHERES;
                    }
                }
                
                visualizer_set_config(vis, &config);
                printf("配置已更新\n");
            } else {
                printf("用法: set <option> <value>\n");
            }
        } else {
            printf("未知命令: %s\n", command);
            printf("输入 'help' 查看可用命令\n");
        }
    }
}

// 主函数
int main(int argc, char** argv) {
    // 解析命令行参数
    parse_arguments(argc, argv);
    
    // 处理帮助和版本信息
    if (options.show_help) {
        show_help();
        return 0;
    }
    
    if (options.show_version) {
        show_version();
        return 0;
    }
    
    // 创建可视化器
    Visualizer* vis = visualizer_create();
    if (!vis) {
        fprintf(stderr, "错误：无法创建可视化器\n");
        return 1;
    }
    
    // 设置配置
    VisualizerConfig config;
    visualizer_get_config(vis, &config);
    
    config.color_scheme = options.color_scheme;
    config.bloch_sphere = !options.no_bloch;
    config.show_phase = !options.no_phase;
    config.show_probabilities = !options.no_probabilities;
    config.animation = !options.no_animation;
    config.vector_representation = options.vector_representation;
    
    visualizer_set_config(vis, &config);
    
    // 设置输出模式
    if (options.output_file) {
        if (!visualizer_set_output_mode(vis, OUTPUT_FILE, options.output_file)) {
            fprintf(stderr, "警告：无法打开输出文件，使用控制台输出\n");
        }
    } else {
        visualizer_set_output_mode(vis, OUTPUT_CONSOLE, NULL);
    }
    
    // 加载或创建量子态
    bool state_loaded = false;
    
    if (options.input_file) {
        // 从文件加载量子态
        int qubit_count;
        complex double* amplitudes = load_quantum_state_from_file(options.input_file, &qubit_count);
        if (amplitudes) {
            visualizer_set_quantum_state(vis, qubit_count, amplitudes);
            printf("已加载量子态: %d 量子比特\n", qubit_count);
            free(amplitudes);
            state_loaded = true;
        }
    } else if (options.example_qubits > 0) {
        // 创建示例量子态
        complex double* amplitudes = create_example_state(options.example_qubits);
        if (amplitudes) {
            visualizer_set_quantum_state(vis, options.example_qubits, amplitudes);
            printf("已创建 %d 量子比特示例态\n", options.example_qubits);
            
            // 为多量子比特态创建纠缠矩阵
            if (options.example_qubits > 1) {
                double** matrix = create_example_entanglement_matrix(options.example_qubits);
                if (matrix) {
                    visualizer_set_entanglement_matrix(vis, options.example_qubits, (const double**)matrix);
                    
                    // 释放矩阵
                    for (int i = 0; i < options.example_qubits; i++) {
                        free(matrix[i]);
                    }
                    free(matrix);
                }
            }
            
            free(amplitudes);
            state_loaded = true;
        }
    }
    
    // 运行交互式模式或可视化量子态
    if (options.interactive) {
        run_interactive_mode(vis);
    } else if (state_loaded) {
        visualizer_visualize(vis);
    } else {
        fprintf(stderr, "错误：未指定量子态文件或示例\n");
        show_help();
    }
    
    // 销毁可视化器
    visualizer_destroy(vis);
    
    return 0;
} 