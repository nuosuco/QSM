// QEntL最小化运行时 - 类型系统模块
// 实现QEntL语言的类型系统和值操作

#include "runtime.h"
#include <stdlib.h>
#include <string.h>
#include <stdio.h>

// ==================== 值创建函数 ====================

Value value_nil(void) {
    Value value;
    value.type = TYPE_NIL;
    return value;
}

Value value_bool(bool b) {
    Value value;
    value.type = TYPE_BOOL;
    value.as.boolean = b;
    return value;
}

Value value_int(int64_t i) {
    Value value;
    value.type = TYPE_INT;
    value.as.integer = i;
    return value;
}

Value value_float(double f) {
    Value value;
    value.type = TYPE_FLOAT;
    value.as.number = f;
    return value;
}

Value value_string(const char* chars, size_t length) {
    Value value;
    value.type = TYPE_STRING;
    
    if (chars == NULL || length == 0) {
        value.as.string.chars = NULL;
        value.as.string.length = 0;
        return value;
    }
    
    // 分配字符串内存
    char* copy = runtime_alloc_string(length);
    if (copy == NULL) {
        // 分配失败，返回空字符串
        value.as.string.chars = NULL;
        value.as.string.length = 0;
        return value;
    }
    
    memcpy(copy, chars, length);
    copy[length] = '\0';
    
    value.as.string.chars = copy;
    value.as.string.length = length;
    return value;
}

Value value_string_copy(const char* chars) {
    if (chars == NULL) {
        return value_string(NULL, 0);
    }
    return value_string(chars, strlen(chars));
}

Value value_array(size_t initial_capacity) {
    Value value;
    value.type = TYPE_ARRAY;
    
    size_t capacity = initial_capacity > 0 ? initial_capacity : 4;
    value.as.array.items = runtime_alloc_value_array(capacity);
    value.as.array.count = 0;
    value.as.array.capacity = capacity;
    
    if (value.as.array.items == NULL) {
        // 分配失败，返回空数组
        value.as.array.capacity = 0;
    }
    
    return value;
}

// ==================== 数组操作 ====================

void value_array_push(Value* array, Value value) {
    if (array->type != TYPE_ARRAY) {
        fprintf(stderr, "错误: 尝试向非数组值添加元素\n");
        return;
    }
    
    // 检查是否需要扩容
    if (array->as.array.count >= array->as.array.capacity) {
        size_t new_capacity = array->as.array.capacity * 2;
        Value* new_items = runtime_realloc_value_array(array->as.array.items, new_capacity);
        if (new_items == NULL) {
            fprintf(stderr, "错误: 数组扩容失败\n");
            return;
        }
        array->as.array.items = new_items;
        array->as.array.capacity = new_capacity;
    }
    
    // 添加新元素
    array->as.array.items[array->as.array.count] = value;
    array->as.array.count++;
}

Value value_array_get(Value* array, size_t index) {
    if (array->type != TYPE_ARRAY) {
        fprintf(stderr, "错误: 尝试从非数组值获取元素\n");
        return value_nil();
    }
    
    if (index >= array->as.array.count) {
        fprintf(stderr, "错误: 数组索引越界: %zu >= %zu\n", index, array->as.array.count);
        return value_nil();
    }
    
    return array->as.array.items[index];
}

void value_array_set(Value* array, size_t index, Value value) {
    if (array->type != TYPE_ARRAY) {
        fprintf(stderr, "错误: 尝试设置非数组值的元素\n");
        return;
    }
    
    if (index >= array->as.array.count) {
        fprintf(stderr, "错误: 数组索引越界: %zu >= %zu\n", index, array->as.array.count);
        return;
    }
    
    array->as.array.items[index] = value;
}

size_t value_array_length(Value* array) {
    if (array->type != TYPE_ARRAY) {
        return 0;
    }
    return array->as.array.count;
}

// ==================== 值类型检查 ====================

bool value_is_nil(Value value) {
    return value.type == TYPE_NIL;
}

bool value_is_bool(Value value) {
    return value.type == TYPE_BOOL;
}

bool value_is_int(Value value) {
    return value.type == TYPE_INT;
}

bool value_is_float(Value value) {
    return value.type == TYPE_FLOAT;
}

bool value_is_string(Value value) {
    return value.type == TYPE_STRING;
}

bool value_is_array(Value value) {
    return value.type == TYPE_ARRAY;
}

// ==================== 值转换 ====================

const char* value_type_name(ValueType type) {
    switch (type) {
        case TYPE_NIL:      return "空值";
        case TYPE_BOOL:     return "布尔";
        case TYPE_INT:      return "整数";
        case TYPE_FLOAT:    return "浮点数";
        case TYPE_STRING:   return "字符串";
        case TYPE_ARRAY:    return "数组";
        case TYPE_MAP:      return "映射";
        case TYPE_FUNCTION: return "函数";
        case TYPE_OBJECT:   return "对象";
        case TYPE_QUANTUM:  return "量子类型";
        default:            return "未知类型";
    }
}

const char* value_to_string(Value value) {
    static char buffer[256];
    
    switch (value.type) {
        case TYPE_NIL:
            return "空值";
            
        case TYPE_BOOL:
            return value.as.boolean ? "真" : "假";
            
        case TYPE_INT:
            snprintf(buffer, sizeof(buffer), "%lld", (long long)value.as.integer);
            return buffer;
            
        case TYPE_FLOAT:
            snprintf(buffer, sizeof(buffer), "%g", value.as.number);
            return buffer;
            
        case TYPE_STRING:
            if (value.as.string.chars == NULL) {
                return "(空字符串)";
            }
            // 如果字符串太长，截断
            if (value.as.string.length < 200) {
                return value.as.string.chars;
            } else {
                snprintf(buffer, sizeof(buffer), "%.200s...", value.as.string.chars);
                return buffer;
            }
            
        case TYPE_ARRAY:
            snprintf(buffer, sizeof(buffer), "数组[%zu]", value.as.array.count);
            return buffer;
            
        default:
            snprintf(buffer, sizeof(buffer), "(%s)", value_type_name(value.type));
            return buffer;
    }
}

// ==================== 值比较 ====================

bool value_equals(Value a, Value b) {
    if (a.type != b.type) return false;
    
    switch (a.type) {
        case TYPE_NIL:
            return true;
            
        case TYPE_BOOL:
            return a.as.boolean == b.as.boolean;
            
        case TYPE_INT:
            return a.as.integer == b.as.integer;
            
        case TYPE_FLOAT:
            return a.as.number == b.as.number;
            
        case TYPE_STRING:
            if (a.as.string.length != b.as.string.length) return false;
            if (a.as.string.chars == NULL && b.as.string.chars == NULL) return true;
            if (a.as.string.chars == NULL || b.as.string.chars == NULL) return false;
            return memcmp(a.as.string.chars, b.as.string.chars, a.as.string.length) == 0;
            
        case TYPE_ARRAY:
            if (a.as.array.count != b.as.array.count) return false;
            // 简化：只比较引用
            return a.as.array.items == b.as.array.items;
            
        default:
            return false;
    }
}

// ==================== 值释放 ====================

void value_free(Value* value) {
    if (value == NULL) return;
    
    switch (value->type) {
        case TYPE_STRING:
            if (value->as.string.chars != NULL) {
                printf("[value_free] 释放字符串: %p (长度: %zu)\n", 
                       value->as.string.chars, value->as.string.length);
                runtime_free_string(value->as.string.chars);
                value->as.string.chars = NULL;
                value->as.string.length = 0;
            } else {
                printf("[value_free] 字符串已为NULL\n");
            }
            break;
            
        case TYPE_ARRAY:
            if (value->as.array.items != NULL) {
                printf("[value_free] 释放数组: %p (数量: %zu)\n",
                       value->as.array.items, value->as.array.count);
                // 递归释放数组元素
                for (size_t i = 0; i < value->as.array.count; i++) {
                    value_free(&value->as.array.items[i]);
                }
                runtime_free(value->as.array.items);
                value->as.array.items = NULL;
                value->as.array.count = 0;
                value->as.array.capacity = 0;
            }
            break;
            
        default:
            // 其他类型不需要特殊释放
            // printf("[value_free] 释放其他类型: %d\n", value->type);
            break;
    }
    
    value->type = TYPE_NIL;
}