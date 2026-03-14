// QEntL运行时 - 数组操作实现
// 版本: 1.0.0

#include "qentl_runtime.h"
#include <stdlib.h>
#include <string.h>
#include <stdio.h>

// ============================================================================
// 内部常量
// ============================================================================

#define ARRAY_DEFAULT_CAPACITY 16
#define ARRAY_GROWTH_FACTOR 2

// ============================================================================
// 内部工具函数
// ============================================================================

static bool array_ensure_capacity(QentlArray* array, size_t min_capacity) {
    if (array->capacity >= min_capacity) {
        return true;
    }
    
    // 计算新容量
    size_t new_capacity = array->capacity;
    if (new_capacity == 0) {
        new_capacity = ARRAY_DEFAULT_CAPACITY;
    }
    
    while (new_capacity < min_capacity) {
        new_capacity *= ARRAY_GROWTH_FACTOR;
        
        // 防止溢出
        if (new_capacity < array->capacity) {
            return false;
        }
    }
    
    // 重新分配内存
    QentlValue* new_elements = (QentlValue*)qentl_realloc(
        array->elements, 
        new_capacity * sizeof(QentlValue)
    );
    
    if (new_elements == NULL) {
        return false;
    }
    
    array->elements = new_elements;
    array->capacity = new_capacity;
    
    return true;
}

// ============================================================================
// 公共API实现
// ============================================================================

QentlArray* qentl_array_create(size_t initial_capacity) {
    QentlArray* array = (QentlArray*)qentl_alloc(sizeof(QentlArray));
    
    if (array == NULL) {
        return NULL;
    }
    
    array->capacity = 0;
    array->length = 0;
    array->elements = NULL;
    
    if (initial_capacity > 0) {
        if (!array_ensure_capacity(array, initial_capacity)) {
            qentl_free(array);
            return NULL;
        }
    }
    
    return array;
}

void qentl_array_destroy(QentlArray* array) {
    if (array == NULL) {
        return;
    }
    
    // 释放所有元素
    for (size_t i = 0; i < array->length; i++) {
        qentl_value_free(array->elements[i]);
    }
    
    // 释放元素数组
    if (array->elements != NULL) {
        qentl_free(array->elements);
    }
    
    // 释放数组结构
    qentl_free(array);
}

void qentl_array_push(QentlArray* array, QentlValue value) {
    if (array == NULL) {
        return;
    }
    
    // 确保有足够容量
    if (!array_ensure_capacity(array, array->length + 1)) {
        printf("❌ [数组] 推送失败: 容量不足\n");
        return;
    }
    
    // 添加元素
    array->elements[array->length] = value;
    array->length++;
}

QentlValue qentl_array_get(QentlArray* array, size_t index) {
    if (array == NULL) {
        return qentl_value_null();
    }
    
    if (index >= array->length) {
        printf("⚠️  [数组] 索引越界: index=%zu, length=%zu\n", index, array->length);
        return qentl_value_null();
    }
    
    return array->elements[index];
}

void qentl_array_set(QentlArray* array, size_t index, QentlValue value) {
    if (array == NULL) {
        return;
    }
    
    if (index >= array->length) {
        printf("⚠️  [数组] 索引越界: index=%zu, length=%zu\n", index, array->length);
        return;
    }
    
    // 释放旧值
    qentl_value_free(array->elements[index]);
    
    // 设置新值
    array->elements[index] = value;
}

size_t qentl_array_length(QentlArray* array) {
    if (array == NULL) {
        return 0;
    }
    return array->length;
}

size_t qentl_array_capacity(QentlArray* array) {
    if (array == NULL) {
        return 0;
    }
    return array->capacity;
}

void qentl_array_clear(QentlArray* array) {
    if (array == NULL) {
        return;
    }
    
    // 释放所有元素
    for (size_t i = 0; i < array->length; i++) {
        qentl_value_free(array->elements[i]);
    }
    
    array->length = 0;
}

// ============================================================================
// 扩展数组操作
// ============================================================================

void qentl_array_insert(QentlArray* array, size_t index, QentlValue value) {
    if (array == NULL) {
        return;
    }
    
    if (index > array->length) {
        index = array->length; // 插入到末尾
    }
    
    // 确保有足够容量
    if (!array_ensure_capacity(array, array->length + 1)) {
        printf("❌ [数组] 插入失败: 容量不足\n");
        return;
    }
    
    // 移动元素
    if (index < array->length) {
        memmove(
            &array->elements[index + 1],
            &array->elements[index],
            (array->length - index) * sizeof(QentlValue)
        );
    }
    
    // 插入新元素
    array->elements[index] = value;
    array->length++;
}

QentlValue qentl_array_pop(QentlArray* array) {
    if (array == NULL || array->length == 0) {
        return qentl_value_null();
    }
    
    array->length--;
    QentlValue value = array->elements[array->length];
    
    return value;
}

QentlValue qentl_array_remove(QentlArray* array, size_t index) {
    if (array == NULL || index >= array->length) {
        return qentl_value_null();
    }
    
    QentlValue value = array->elements[index];
    
    // 移动元素
    if (index < array->length - 1) {
        memmove(
            &array->elements[index],
            &array->elements[index + 1],
            (array->length - index - 1) * sizeof(QentlValue)
        );
    }
    
    array->length--;
    return value;
}

bool qentl_array_contains(QentlArray* array, QentlValue value) {
    if (array == NULL) {
        return false;
    }
    
    // 简化实现：只检查指针相等
    // 实际应该使用值比较
    for (size_t i = 0; i < array->length; i++) {
        if (array->elements[i].type == value.type) {
            switch (value.type) {
                case QENTL_TYPE_NULL:
                    return true; // 所有null都相等
                    
                case QENTL_TYPE_BOOLEAN:
                    if (array->elements[i].data.boolean == value.data.boolean) {
                        return true;
                    }
                    break;
                    
                case QENTL_TYPE_INTEGER:
                    if (array->elements[i].data.integer == value.data.integer) {
                        return true;
                    }
                    break;
                    
                case QENTL_TYPE_FLOAT:
                    if (array->elements[i].data.floating == value.data.floating) {
                        return true;
                    }
                    break;
                    
                case QENTL_TYPE_STRING:
                    if (strcmp((char*)array->elements[i].data.pointer, 
                              (char*)value.data.pointer) == 0) {
                        return true;
                    }
                    break;
                    
                default:
                    // 对于其他类型，检查指针相等
                    if (array->elements[i].data.pointer == value.data.pointer) {
                        return true;
                    }
            }
        }
    }
    
    return false;
}

QentlArray* qentl_array_slice(QentlArray* array, size_t start, size_t length) {
    if (array == NULL) {
        return qentl_array_create(0);
    }
    
    // 检查边界
    if (start >= array->length) {
        return qentl_array_create(0);
    }
    
    if (start + length > array->length) {
        length = array->length - start;
    }
    
    // 创建新数组
    QentlArray* slice = qentl_array_create(length);
    if (slice == NULL) {
        return NULL;
    }
    
    // 复制元素（需要克隆值）
    for (size_t i = 0; i < length; i++) {
        QentlValue original = array->elements[start + i];
        QentlValue cloned = qentl_value_clone(original);
        qentl_array_push(slice, cloned);
    }
    
    return slice;
}

void qentl_array_reverse(QentlArray* array) {
    if (array == NULL || array->length < 2) {
        return;
    }
    
    size_t left = 0;
    size_t right = array->length - 1;
    
    while (left < right) {
        // 交换元素
        QentlValue temp = array->elements[left];
        array->elements[left] = array->elements[right];
        array->elements[right] = temp;
        
        left++;
        right--;
    }
}

QentlArray* qentl_array_concat(QentlArray* array1, QentlArray* array2) {
    size_t len1 = array1 ? array1->length : 0;
    size_t len2 = array2 ? array2->length : 0;
    size_t total_len = len1 + len2;
    
    QentlArray* result = qentl_array_create(total_len);
    if (result == NULL) {
        return NULL;
    }
    
    // 复制第一个数组
    if (array1 != NULL) {
        for (size_t i = 0; i < len1; i++) {
            QentlValue cloned = qentl_value_clone(array1->elements[i]);
            qentl_array_push(result, cloned);
        }
    }
    
    // 复制第二个数组
    if (array2 != NULL) {
        for (size_t i = 0; i < len2; i++) {
            QentlValue cloned = qentl_value_clone(array2->elements[i]);
            qentl_array_push(result, cloned);
        }
    }
    
    return result;
}

// ============================================================================
// 调试函数
// ============================================================================

void qentl_array_dump(QentlArray* array) {
    if (array == NULL) {
        printf("[数组] NULL\n");
        return;
    }
    
    printf("[数组] length=%zu, capacity=%zu\n", array->length, array->capacity);
    
    for (size_t i = 0; i < array->length; i++) {
        QentlValue value = array->elements[i];
        char* str = qentl_value_to_string(value);
        printf("  [%zu]: %s\n", i, str);
        qentl_string_free(str);
    }
}