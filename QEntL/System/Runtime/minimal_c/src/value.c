// QEntL最小化运行时 - 值操作模块
// 补充值操作辅助函数

#include "runtime.h"
#include <stdio.h>
#include <string.h>
#include <math.h>
#include <stdlib.h>

// ==================== 值类型检查 ====================

bool value_is_number(Value value) {
    return value.type == TYPE_INT || value.type == TYPE_FLOAT;
}

bool value_is_truthy(Value value) {
    switch (value.type) {
        case TYPE_NIL:
            return false;
        case TYPE_BOOL:
            return value.as.boolean;
        case TYPE_INT:
            return value.as.integer != 0;
        case TYPE_FLOAT:
            return value.as.number != 0.0;
        case TYPE_STRING:
            return value.as.string.length > 0;
        case TYPE_ARRAY:
            return value.as.array.count > 0;
        default:
            return true; // 其他类型视为真
    }
}

// ==================== 数值转换 ====================

double value_to_number(Value value) {
    switch (value.type) {
        case TYPE_NIL:
            return 0.0;
        case TYPE_BOOL:
            return value.as.boolean ? 1.0 : 0.0;
        case TYPE_INT:
            return (double)value.as.integer;
        case TYPE_FLOAT:
            return value.as.number;
        case TYPE_STRING:
            // 简单字符串转数字（简化实现）
            if (value.as.string.chars == NULL) return 0.0;
            return atof(value.as.string.chars);
        default:
            return 0.0;
    }
}

int64_t value_to_int(Value value) {
    switch (value.type) {
        case TYPE_NIL:
            return 0;
        case TYPE_BOOL:
            return value.as.boolean ? 1 : 0;
        case TYPE_INT:
            return value.as.integer;
        case TYPE_FLOAT:
            return (int64_t)value.as.number;
        case TYPE_STRING:
            if (value.as.string.chars == NULL) return 0;
            return atoll(value.as.string.chars);
        default:
            return 0;
    }
}

// ==================== 数值运算 ====================

Value value_add(Value a, Value b) {
    if (value_is_int(a) && value_is_int(b)) {
        return value_int(a.as.integer + b.as.integer);
    }
    
    double a_num = value_to_number(a);
    double b_num = value_to_number(b);
    return value_float(a_num + b_num);
}

Value value_sub(Value a, Value b) {
    if (value_is_int(a) && value_is_int(b)) {
        return value_int(a.as.integer - b.as.integer);
    }
    
    double a_num = value_to_number(a);
    double b_num = value_to_number(b);
    return value_float(a_num - b_num);
}

Value value_mul(Value a, Value b) {
    if (value_is_int(a) && value_is_int(b)) {
        return value_int(a.as.integer * b.as.integer);
    }
    
    double a_num = value_to_number(a);
    double b_num = value_to_number(b);
    return value_float(a_num * b_num);
}

Value value_div(Value a, Value b) {
    double b_num = value_to_number(b);
    if (b_num == 0.0) {
        fprintf(stderr, "除零错误\n");
        return value_nil();
    }
    
    double a_num = value_to_number(a);
    return value_float(a_num / b_num);
}

Value value_mod(Value a, Value b) {
    if (value_is_int(a) && value_is_int(b)) {
        if (b.as.integer == 0) {
            fprintf(stderr, "取模零错误\n");
            return value_nil();
        }
        return value_int(a.as.integer % b.as.integer);
    }
    
    // 浮点数取模（简化实现）
    double a_num = value_to_number(a);
    double b_num = value_to_number(b);
    if (b_num == 0.0) {
        fprintf(stderr, "取模零错误\n");
        return value_nil();
    }
    return value_float(fmod(a_num, b_num));
}

Value value_neg(Value a) {
    if (value_is_int(a)) {
        return value_int(-a.as.integer);
    }
    
    double num = value_to_number(a);
    return value_float(-num);
}

// ==================== 比较运算 ====================

bool value_lt(Value a, Value b) {
    if (value_is_number(a) && value_is_number(b)) {
        double a_num = value_to_number(a);
        double b_num = value_to_number(b);
        return a_num < b_num;
    }
    
    // 字符串比较
    if (value_is_string(a) && value_is_string(b)) {
        if (a.as.string.chars == NULL || b.as.string.chars == NULL) {
            return false;
        }
        return strcmp(a.as.string.chars, b.as.string.chars) < 0;
    }
    
    return false;
}

bool value_le(Value a, Value b) {
    if (value_is_number(a) && value_is_number(b)) {
        double a_num = value_to_number(a);
        double b_num = value_to_number(b);
        return a_num <= b_num;
    }
    
    // 字符串比较
    if (value_is_string(a) && value_is_string(b)) {
        if (a.as.string.chars == NULL || b.as.string.chars == NULL) {
            return a.as.string.chars == b.as.string.chars;
        }
        return strcmp(a.as.string.chars, b.as.string.chars) <= 0;
    }
    
    return false;
}

bool value_gt(Value a, Value b) {
    return !value_le(a, b);
}

bool value_ge(Value a, Value b) {
    return !value_lt(a, b);
}

// ==================== 逻辑运算 ====================

Value value_not(Value a) {
    return value_bool(!value_is_truthy(a));
}

Value value_and(Value a, Value b) {
    return value_bool(value_is_truthy(a) && value_is_truthy(b));
}

Value value_or(Value a, Value b) {
    return value_bool(value_is_truthy(a) || value_is_truthy(b));
}

// ==================== 字符串操作 ====================

Value value_string_concat(Value a, Value b) {
    if (!value_is_string(a) || !value_is_string(b)) {
        fprintf(stderr, "字符串连接操作数类型错误\n");
        return value_nil();
    }
    
    const char* a_str = a.as.string.chars ? a.as.string.chars : "";
    const char* b_str = b.as.string.chars ? b.as.string.chars : "";
    
    size_t a_len = a.as.string.length;
    size_t b_len = b.as.string.length;
    size_t total_len = a_len + b_len;
    
    char* combined = runtime_alloc_string(total_len);
    if (combined == NULL) {
        return value_nil();
    }
    
    memcpy(combined, a_str, a_len);
    memcpy(combined + a_len, b_str, b_len);
    combined[total_len] = '\0';
    
    return value_string(combined, total_len);
}

bool value_string_equals(Value a, Value b) {
    if (!value_is_string(a) || !value_is_string(b)) {
        return false;
    }
    
    if (a.as.string.length != b.as.string.length) {
        return false;
    }
    
    if (a.as.string.chars == NULL && b.as.string.chars == NULL) {
        return true;
    }
    
    if (a.as.string.chars == NULL || b.as.string.chars == NULL) {
        return false;
    }
    
    return memcmp(a.as.string.chars, b.as.string.chars, a.as.string.length) == 0;
}

// ==================== 数组操作 ====================

Value value_array_slice(Value* array, size_t start, size_t end) {
    if (!value_is_array(*array)) {
        fprintf(stderr, "切片操作数不是数组\n");
        return value_nil();
    }
    
    if (start > end || end > array->as.array.count) {
        fprintf(stderr, "切片索引越界: %zu-%zu (数组大小: %zu)\n", 
                start, end, array->as.array.count);
        return value_nil();
    }
    
    Value result = value_array(end - start);
    if (!value_is_array(result)) {
        return value_nil();
    }
    
    for (size_t i = start; i < end; i++) {
        value_array_push(&result, array->as.array.items[i]);
    }
    
    return result;
}

void value_array_clear(Value* array) {
    if (!value_is_array(*array)) {
        return;
    }
    
    // 释放所有元素
    for (size_t i = 0; i < array->as.array.count; i++) {
        value_free(&array->as.array.items[i]);
    }
    
    array->as.array.count = 0;
}

// ==================== 值复制 ====================

Value value_copy(Value value) {
    switch (value.type) {
        case TYPE_NIL:
        case TYPE_BOOL:
        case TYPE_INT:
        case TYPE_FLOAT:
            return value; // 基本类型直接复制
            
        case TYPE_STRING:
            return value_string(value.as.string.chars, value.as.string.length);
            
        case TYPE_ARRAY: {
            Value copy = value_array(value.as.array.capacity);
            if (!value_is_array(copy)) {
                return value_nil();
            }
            
            // 深度复制数组元素
            for (size_t i = 0; i < value.as.array.count; i++) {
                Value element_copy = value_copy(value.as.array.items[i]);
                value_array_push(&copy, element_copy);
            }
            
            return copy;
        }
            
        default:
            // 其他类型暂不支持复制
            return value_nil();
    }
}

// ==================== 调试输出 ====================

void value_print(Value value) {
    const char* str = value_to_string(value);
    printf("%s", str);
}

void value_println(Value value) {
    value_print(value);
    printf("\n");
}