/**
 * @file output_element_processor.c
 * @brief 输出元素处理器实现
 * @author Claude
 * @version 1.0
 * @date 2024-05-31
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <math.h>
#include "../../include/quantum_gene.h"
#include "../../include/quantum_state.h"
#include "../../include/quantum_field.h"

/**
 * @brief 输出元素类型
 */
typedef enum {
    OUTPUT_ELEMENT_TEXT,           /* 文本元素 */
    OUTPUT_ELEMENT_IMAGE,          /* 图像元素 */
    OUTPUT_ELEMENT_AUDIO,          /* 音频元素 */
    OUTPUT_ELEMENT_VECTOR,         /* 向量元素 */
    OUTPUT_ELEMENT_COMPLEX         /* 复合元素 */
} OutputElementType;

/**
 * @brief 输出元素结构体定义
 */
typedef struct {
    OutputElementType type;        /* 元素类型 */
    void *data;                    /* 元素数据 */
    size_t data_size;              /* 数据大小 */
    char name[64];                 /* 元素名称 */
    double quality;                /* 元素质量因子 */
    int processed;                 /* 是否已处理 */
    void *metadata;                /* 元素元数据 */
} OutputElement;

/**
 * @brief 输出元素处理器结构体
 */
typedef struct {
    int processing_level;          /* 处理级别 (1-3) */
    int element_count;             /* 元素数量 */
    OutputElement **elements;      /* 元素数组 */
    double scale_factor;           /* 缩放因子 */
    char output_format[32];        /* 输出格式 */
    void *transformation_context;  /* 转换上下文 */
} OutputElementProcessor;

/**
 * @brief 创建输出元素处理器
 * 
 * @param processing_level 处理级别 (1: 基础, 2: 标准, 3: 高级)
 * @return OutputElementProcessor* 处理器指针
 */
OutputElementProcessor* output_element_processor_create(int processing_level) {
    if (processing_level < 1 || processing_level > 3) {
        fprintf(stderr, "错误: 处理级别必须在1-3范围内\n");
        return NULL;
    }

    OutputElementProcessor *processor = (OutputElementProcessor*)malloc(sizeof(OutputElementProcessor));
    if (!processor) {
        fprintf(stderr, "错误: 无法分配输出元素处理器内存\n");
        return NULL;
    }

    processor->processing_level = processing_level;
    processor->element_count = 0;
    processor->elements = NULL;
    processor->scale_factor = 1.0;
    processor->transformation_context = NULL;
    
    // 设置默认输出格式
    strcpy(processor->output_format, "Standard");
    
    printf("创建了输出元素处理器，处理级别 %d\n", processing_level);
    
    return processor;
}

/**
 * @brief 销毁输出元素处理器
 * 
 * @param processor 处理器指针
 */
void output_element_processor_destroy(OutputElementProcessor *processor) {
    if (!processor) return;
    
    // 释放所有元素
    for (int i = 0; i < processor->element_count; i++) {
        if (processor->elements[i]) {
            if (processor->elements[i]->data) {
                free(processor->elements[i]->data);
            }
            if (processor->elements[i]->metadata) {
                free(processor->elements[i]->metadata);
            }
            free(processor->elements[i]);
        }
    }
    
    // 释放元素数组
    if (processor->elements) {
        free(processor->elements);
    }
    
    // 释放转换上下文
    if (processor->transformation_context) {
        free(processor->transformation_context);
    }
    
    free(processor);
    printf("销毁了输出元素处理器\n");
}

/**
 * @brief 创建输出元素
 * 
 * @param type 元素类型
 * @param name 元素名称
 * @param data 元素数据
 * @param data_size 数据大小
 * @return OutputElement* 元素指针
 */
OutputElement* output_element_create(OutputElementType type, const char *name, 
                                    const void *data, size_t data_size) {
    if (!name || (!data && data_size > 0)) {
        return NULL;
    }
    
    OutputElement *element = (OutputElement*)malloc(sizeof(OutputElement));
    if (!element) {
        fprintf(stderr, "错误: 无法分配输出元素内存\n");
        return NULL;
    }
    
    element->type = type;
    strncpy(element->name, name, sizeof(element->name) - 1);
    element->name[sizeof(element->name) - 1] = '\0';
    
    element->quality = 1.0; // 默认质量
    element->processed = 0;
    element->metadata = NULL;
    
    // 复制数据
    if (data && data_size > 0) {
        element->data = malloc(data_size);
        if (!element->data) {
            fprintf(stderr, "错误: 无法分配元素数据内存\n");
            free(element);
            return NULL;
        }
        memcpy(element->data, data, data_size);
        element->data_size = data_size;
    } else {
        element->data = NULL;
        element->data_size = 0;
    }
    
    return element;
}

/**
 * @brief 添加输出元素到处理器
 * 
 * @param processor 处理器指针
 * @param element 元素指针
 * @return int 成功返回元素索引，失败返回-1
 */
int output_element_processor_add_element(OutputElementProcessor *processor, OutputElement *element) {
    if (!processor || !element) {
        return -1;
    }
    
    // 扩展元素数组
    OutputElement **new_elements = (OutputElement**)realloc(
        processor->elements, 
        (processor->element_count + 1) * sizeof(OutputElement*)
    );
    
    if (!new_elements) {
        fprintf(stderr, "错误: 无法重新分配元素数组内存\n");
        return -1;
    }
    
    processor->elements = new_elements;
    processor->elements[processor->element_count] = element;
    
    printf("添加了输出元素'%s'，类型 %d\n", element->name, element->type);
    
    return processor->element_count++;
}

/**
 * @brief 从量子基因创建输出元素
 * 
 * @param processor 处理器指针
 * @param gene 量子基因
 * @param element_type 元素类型
 * @param element_name 元素名称
 * @return OutputElement* 创建的元素指针
 */
OutputElement* output_element_processor_create_from_gene(OutputElementProcessor *processor, 
                                                      const QuantumGene *gene,
                                                      OutputElementType element_type,
                                                      const char *element_name) {
    if (!processor || !gene || !element_name) {
        return NULL;
    }
    
    // 根据基因长度分配数据缓冲区
    size_t data_size = gene->length / 8 + (gene->length % 8 ? 1 : 0);
    uint8_t *data = (uint8_t*)calloc(data_size, 1);
    if (!data) {
        fprintf(stderr, "错误: 无法分配元素数据缓冲区\n");
        return NULL;
    }
    
    // 将基因编码为二进制数
    for (size_t i = 0; i < gene->length; i++) {
        // 使用基因元素的振幅作为概率
        double probability = gene->elements[i].amplitude[0] * gene->elements[i].amplitude[0];
        int bit_value = probability > 0.5 ? 1 : 0;
        
        // 设置相应位
        if (bit_value) {
            data[i / 8] |= (1 << (i % 8));
        }
    }
    
    // 创建输出元素
    OutputElement *element = output_element_create(element_type, element_name, data, data_size);
    free(data); // 释放临时缓冲区
    
    if (element) {
        // 根据处理级别设置元素质量
        switch (processor->processing_level) {
            case 1:
                element->quality = 0.8;
                break;
            case 2:
                element->quality = 0.9;
                break;
            case 3:
                element->quality = 0.98;
                break;
        }
    }
    
    return element;
}

/**
 * @brief 转换输出元素类型
 * 
 * @param processor 处理器指针
 * @param element 元素指针
 * @param new_type 新元素类型
 * @return int 成功返回0，失败返回非0值
 */
int output_element_processor_convert_type(OutputElementProcessor *processor, 
                                       OutputElement *element,
                                       OutputElementType new_type) {
    if (!processor || !element) {
        return -1;
    }
    
    if (element->type == new_type) {
        return 0; // 已经是目标类型
    }
    
    // 转换过程依赖于源类型和目标类型
    void *new_data = NULL;
    size_t new_size = 0;
    
    // 示例转换：从文本转换为向量
    if (element->type == OUTPUT_ELEMENT_TEXT && new_type == OUTPUT_ELEMENT_VECTOR) {
        // 创建一个简单的向量表示
        size_t vector_size = element->data_size * sizeof(double);
        new_data = malloc(vector_size);
        if (!new_data) {
            fprintf(stderr, "错误: 无法分配新元素数据内存\n");
            return -1;
        }
        
        // 简单转换：将ASCII值转换为向量元素
        double *vector = (double*)new_data;
        uint8_t *text = (uint8_t*)element->data;
        for (size_t i = 0; i < element->data_size; i++) {
            vector[i] = (double)text[i] / 255.0;
        }
        
        new_size = vector_size;
    } 
    // 其他类型转换...
    else {
        fprintf(stderr, "错误: 不支持从类型 %d 到类型%d 的转换\n", 
                element->type, new_type);
        return -1;
    }
    
    // 更新元素数据
    if (new_data) {
        if (element->data) {
            free(element->data);
        }
        
        element->data = new_data;
        element->data_size = new_size;
        element->type = new_type;
        return 0;
    }
    
    return -1;
}

/**
 * @brief 处理输出元素
 * 
 * @param processor 处理器指针
 * @param element_index 元素索引
 * @return int 成功返回0，失败返回非0值
 */
int output_element_processor_process(OutputElementProcessor *processor, int element_index) {
    if (!processor || element_index < 0 || element_index >= processor->element_count) {
        return -1;
    }
    
    OutputElement *element = processor->elements[element_index];
    if (!element || element->processed) {
        return -1;
    }
    
    // 根据元素类型和处理级别进行处理
    switch (element->type) {
        case OUTPUT_ELEMENT_TEXT:
            // 文本处理：大小写转换、修剪等
            {
                char *text = (char*)element->data;
                size_t len = element->data_size;
                
                if (processor->processing_level >= 2) {
                    // 移除前后空白
                    int start = 0, end = len - 1;
                    while (start < len && (text[start] == ' ' || text[start] == '\t' || 
                           text[start] == '\n' || text[start] == '\r')) {
                        start++;
                    }
                    
                    while (end >= start && (text[end] == ' ' || text[end] == '\t' || 
                           text[end] == '\n' || text[end] == '\r')) {
                        end--;
                    }
                    
                    if (start > 0 || end < len - 1) {
                        size_t new_len = end - start + 1;
                        memmove(text, text + start, new_len);
                        text[new_len] = '\0';
                        element->data_size = new_len + 1;
                    }
                }
            }
            break;
            
        case OUTPUT_ELEMENT_IMAGE:
            // 图像处理：尺寸调整、滤镜等
            // 简化实现- 仅表明处理过
            printf("处理图像元素 '%s'，应用处理级别%d\n", 
                   element->name, processor->processing_level);
            break;
            
        case OUTPUT_ELEMENT_AUDIO:
            // 音频处理：标准化、压缩等
            // 简化实现- 仅表明处理过
            printf("处理音频元素 '%s'，应用处理级别%d\n", 
                   element->name, processor->processing_level);
            break;
            
        case OUTPUT_ELEMENT_VECTOR:
            // 向量处理：归一化等
            {
                double *vector = (double*)element->data;
                size_t count = element->data_size / sizeof(double);
                
                if (processor->processing_level >= 2) {
                    // 向量归一化
                    double sum_squares = 0.0;
                    for (size_t i = 0; i < count; i++) {
                        sum_squares += vector[i] * vector[i];
                    }
                    
                    double norm = sqrt(sum_squares);
                    if (norm > 0.0001) {
                        for (size_t i = 0; i < count; i++) {
                            vector[i] /= norm;
                        }
                    }
                }
            }
            break;
            
        case OUTPUT_ELEMENT_COMPLEX:
            // 复合元素处理
            // 简化实现- 仅表明处理过
            printf("处理复合元素 '%s'，应用处理级别%d\n", 
                   element->name, processor->processing_level);
            break;
    }
    
    // 应用全局缩放
    if (processor->scale_factor != 1.0) {
        // 根据元素类型应用缩放
        // 仅做简化处理
        printf("应用缩放因子 %.2f 到元素'%s'\n", 
               processor->scale_factor, element->name);
    }
    
    element->processed = 1;
    return 0;
}

/**
 * @brief 将元素转换为量子场
 * 
 * @param processor 处理器指针
 * @param element_index 元素索引
 * @return QField* 生成的量子场
 */
QField* output_element_processor_to_quantum_field(OutputElementProcessor *processor,
                                                      int element_index) {
    if (!processor || element_index < 0 || element_index >= processor->element_count) {
        return NULL;
    }
    
    OutputElement *element = processor->elements[element_index];
    if (!element) {
        return NULL;
    }
    
    // 确保元素已处理
    if (!element->processed) {
        output_element_processor_process(processor, element_index);
    }
    
    // 根据元素类型创建适当的量子场
    // 简化实现：创建1D或2D
    int dimension = 1;
    int dimensions[2] = {1, 1};
    
    switch (element->type) {
        case OUTPUT_ELEMENT_TEXT:
            // 文本元素可视为一维场
            dimension = 1;
            dimensions[0] = element->data_size;
            break;
            
        case OUTPUT_ELEMENT_IMAGE:
            // 图像元素可视为二维场
            dimension = 2;
            // 假设是方形图像
            dimensions[0] = dimensions[1] = (int)sqrt(element->data_size);
            break;
            
        case OUTPUT_ELEMENT_AUDIO:
            // 音频元素可视为一维场
            dimension = 1;
            dimensions[0] = element->data_size;
            break;
            
        case OUTPUT_ELEMENT_VECTOR:
            // 向量元素通常是一维的
            dimension = 1;
            dimensions[0] = element->data_size / sizeof(double);
            break;
            
        case OUTPUT_ELEMENT_COMPLEX:
            // 复杂元素可能需要更多维度
            dimension = 2;
            dimensions[0] = dimensions[1] = (int)sqrt(element->data_size);
            break;
    }
    
    // 创建量子场
    QField *field = quantum_field_create("元素场", FIELD_TYPE_PROBABILISTIC);
    if (!field) {
        return NULL;
    }
    
    // 初始化场数据
    for (int i = 0; i < dimensions[0]; i++) {
        int index = i;
        double value = 0.0;
        
        // 根据元素类型提取数据
        if (element->type == OUTPUT_ELEMENT_VECTOR) {
            if (i < element->data_size / sizeof(double)) {
                value = ((double*)element->data)[i];
            }
        } else if (element->type == OUTPUT_ELEMENT_IMAGE && dimension == 2) {
            for (int j = 0; j < dimensions[1]; j++) {
                index = i * dimensions[1] + j;
                if (index < element->data_size) {
                    value = ((uint8_t*)element->data)[index] / 255.0;
                    
                    // 创建场节点
                    QFieldNode node;
                    node.x = i;
                    node.y = j;
                    node.z = 0.0;
                    node.intensity = value;
                    node.state = NULL;
                    node.position = NULL;
                    
                    quantum_field_add_node(field, &node);
                }
            }
        } else {
            // 其他类型的简化处理
            if (i < element->data_size) {
                value = ((uint8_t*)element->data)[i] / 255.0;
                
                // 创建场节点
                QFieldNode node;
                node.x = i;
                node.y = 0.0;
                node.z = 0.0;
                node.intensity = value;
                node.state = NULL;
                node.position = NULL;
                
                quantum_field_add_node(field, &node);
            }
        }
    }
    
    printf("创建了从元素 '%s' 转换得到的量子场，维度 %d\n", 
            element->name, dimension);
    
    return field;
}

/**
 * @brief 批处理所有元素
 * 
 * @param processor 处理器指针
 * @return int 成功处理的元素数量
 */
int output_element_processor_process_all(OutputElementProcessor *processor) {
    if (!processor) return 0;
    
    int success_count = 0;
    
    for (int i = 0; i < processor->element_count; i++) {
        if (output_element_processor_process(processor, i) == 0) {
            success_count++;
        }
    }
    
    printf("批处理了 %d 个元素，成功: %d\n", 
           processor->element_count, success_count);
    
    return success_count;
}

/**
 * @brief 设置输出格式
 * 
 * @param processor 处理器指针
 * @param format 格式名称
 * @return int 成功返回0，失败返回非0值
 */
int output_element_processor_set_format(OutputElementProcessor *processor, const char *format) {
    if (!processor || !format) {
        return -1;
    }
    
    strncpy(processor->output_format, format, sizeof(processor->output_format) - 1);
    processor->output_format[sizeof(processor->output_format) - 1] = '\0';
    
    printf("设置输出格式为 %s\n", processor->output_format);
    
    return 0;
}

/**
 * @brief 设置缩放因子
 * 
 * @param processor 处理器指针
 * @param scale_factor 缩放因子
 * @return int 成功返回0，失败返回非0值
 */
int output_element_processor_set_scale_factor(OutputElementProcessor *processor, double scale_factor) {
    if (!processor || scale_factor <= 0.0) {
        return -1;
    }
    
    processor->scale_factor = scale_factor;
    printf("设置缩放因子为 %.2f\n", scale_factor);
    
    return 0;
}

/**
 * @brief 获取元素数据
 * 
 * @param processor 处理器指针
 * @param element_index 元素索引
 * @param data_out 输出数据指针的指针
 * @param size_out 输出数据大小的指针
 * @return int 成功返回0，失败返回非0值
 */
int output_element_processor_get_data(OutputElementProcessor *processor, 
                                    int element_index,
                                    void **data_out, 
                                    size_t *size_out) {
    if (!processor || element_index < 0 || element_index >= processor->element_count || 
        !data_out || !size_out) {
        return -1;
    }
    
    OutputElement *element = processor->elements[element_index];
    if (!element) {
        return -1;
    }
    
    // 确保元素已处理
    if (!element->processed) {
        output_element_processor_process(processor, element_index);
    }
    
    *data_out = element->data;
    *size_out = element->data_size;
    
    return 0;
}

/**
 * @brief 将量子场保存为XML文件
 * 
 * @param field 量子场
 * @param filename 文件名
 * @return int 成功返回0，失败返回非0值
 */
int output_element_processor_save_quantum_field(QField *field, const char *filename) {
    if (!field || !filename) {
        return -1;
    }
    
    FILE *output_file = fopen(filename, "w");
    if (!output_file) {
        fprintf(stderr, "错误: 无法打开输出文件\n");
        return -1;
    }
    
    switch (field->type) {
        case OUTPUT_FORMAT_XML:
            fprintf(output_file, "<QField>\n");
            fprintf(output_file, "  <Name>%s</Name>\n", field->name);
            fprintf(output_file, "  <Type>%d</Type>\n", field->type);
            fprintf(output_file, "  <Dimension>%d</Dimension>\n", field->dimension);
            fprintf(output_file, "  <Intensity>%.4f</Intensity>\n", field->intensity);
            fprintf(output_file, "  <NodeCount>%d</NodeCount>\n", field->node_count);
            
            fprintf(output_file, "  <Nodes>\n");
            for (int i = 0; i < field->node_count; i++) {
                fprintf(output_file, "    <Node>\n");
                fprintf(output_file, "      <Position>\n");
                fprintf(output_file, "        <X>%.4f</X>\n", field->nodes[i].x);
                fprintf(output_file, "        <Y>%.4f</Y>\n", field->nodes[i].y);
                fprintf(output_file, "        <Z>%.4f</Z>\n", field->nodes[i].z);
                fprintf(output_file, "      </Position>\n");
                fprintf(output_file, "      <Intensity>%.4f</Intensity>\n", field->nodes[i].intensity);
                fprintf(output_file, "    </Node>\n");
            }
            fprintf(output_file, "  </Nodes>\n");
            fprintf(output_file, "</QField>\n");
            break;
            
        default:
            fprintf(stderr, "错误: 不支持的量子场类型\n");
            fclose(output_file);
            return -1;
    }
    
    fclose(output_file);
    printf("量子场保存到文件: %s\n", filename);
    
    return 0;
} 
