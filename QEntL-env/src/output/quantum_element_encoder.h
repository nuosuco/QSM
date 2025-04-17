/*
 * 元素量子编码系统头文件
 * 负责为各类输出元素自动添加量子基因编码和量子纠缠信道
 */

// 量子基因编码
// QG-SRC-QENCODER-H-A1B1

#ifndef QUANTUM_ELEMENT_ENCODER_H
#define QUANTUM_ELEMENT_ENCODER_H

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "../quantum_gene.h"
#include "../quantum_entanglement.h"

// 输出元素类型
typedef enum {
    ELEMENT_TYPE_TEXT,        // 文本元素
    ELEMENT_TYPE_CODE,        // 代码元素
    ELEMENT_TYPE_IMAGE,       // 图像元素
    ELEMENT_TYPE_AUDIO,       // 音频元素
    ELEMENT_TYPE_VIDEO,       // 视频元素
    ELEMENT_TYPE_DOCUMENT,    // 文档元素
    ELEMENT_TYPE_BINARY,      // 二进制元素
    ELEMENT_TYPE_STRUCTURED,  // 结构化数据元素
    ELEMENT_TYPE_QUANTUM_STATE // 量子状态元素
} ElementType;

// 编码位置
typedef enum {
    ENCODE_POSITION_HEADER,    // 在元素头部编码
    ENCODE_POSITION_FOOTER,    // 在元素尾部编码
    ENCODE_POSITION_EMBEDDED,  // 嵌入元素内部
    ENCODE_POSITION_METADATA   // 在元素元数据中编码
} EncodePosition;

// 编码配置
typedef struct {
    int auto_encode_enabled;          // 是否启用自动编码
    EncodePosition encode_position;   // 编码位置
    int include_entanglement_channel; // 是否包含纠缠信道
    int preserve_format;              // 是否保留原始格式
    int add_checksum;                 // 是否添加校验和
    double encode_strength;           // 编码强度(0.0-1.0)
    char encoding_prefix[32];         // 编码前缀
    char encoding_suffix[32];         // 编码后缀
} ElementEncoderConfig;

// 元素编码器
typedef struct {
    char id[64];                       // 编码器ID
    ElementEncoderConfig config;       // 编码配置
    int encoded_elements_count;        // 已编码元素计数
    time_t creation_time;              // 创建时间
    QuantumGene* encoder_gene;         // 编码器基因标记
} QuantumElementEncoder;

// 编码元素内容
typedef struct {
    void* data;              // 数据指针
    size_t size;             // 数据大小
    ElementType type;        // 元素类型
    char* metadata;          // 元数据
    QuantumGene* gene;       // 量子基因
    EntanglementChannel* channel; // 量子纠缠信道
} EncodedElement;

// 创建元素编码器
QuantumElementEncoder* quantum_element_encoder_create(const char* id);

// 销毁元素编码器
void quantum_element_encoder_destroy(QuantumElementEncoder* encoder);

// 配置元素编码器
void quantum_element_encoder_configure(QuantumElementEncoder* encoder, ElementEncoderConfig* config);

// 编码文本元素
char* quantum_element_encoder_encode_text(
    QuantumElementEncoder* encoder,
    const char* text,
    const char* gene_code
);

// 编码代码元素
char* quantum_element_encoder_encode_code(
    QuantumElementEncoder* encoder,
    const char* code,
    const char* language,
    const char* gene_code
);

// 编码图像元素
void* quantum_element_encoder_encode_image(
    QuantumElementEncoder* encoder,
    void* image_data,
    size_t image_size,
    const char* format,
    const char* gene_code,
    size_t* result_size
);

// 编码量子状态
QuantumState* quantum_element_encoder_encode_quantum_state(
    QuantumElementEncoder* encoder,
    QuantumState* state,
    const char* gene_code
);

// 编码任意元素
EncodedElement* quantum_element_encoder_encode_element(
    QuantumElementEncoder* encoder,
    void* data,
    size_t size,
    ElementType type,
    const char* gene_code
);

// 从编码元素提取量子基因
QuantumGene* quantum_element_encoder_extract_gene(
    QuantumElementEncoder* encoder,
    void* encoded_data,
    size_t data_size,
    ElementType type
);

// 检查元素是否包含量子编码
int quantum_element_encoder_has_encoding(
    QuantumElementEncoder* encoder,
    void* data,
    size_t size,
    ElementType type
);

// 自动为所有输出的元素应用量子编码
void quantum_element_encoder_auto_encode(
    QuantumElementEncoder* encoder,
    int enabled
);

// 自动生成量子基因代码
char* quantum_element_encoder_generate_gene_code(
    QuantumElementEncoder* encoder,
    ElementType type,
    const char* context_info
);

// 从编码元素建立量子纠缠信道
EntanglementChannel* quantum_element_encoder_create_channel_from_element(
    QuantumElementEncoder* encoder,
    EncodedElement* element,
    QuantumState* state
);

// 释放编码元素
void quantum_element_encoder_free_encoded_element(
    EncodedElement* element
);

// 获取编码统计信息
int quantum_element_encoder_get_encoded_count(
    QuantumElementEncoder* encoder
);

#endif /* QUANTUM_ELEMENT_ENCODER_H */ 