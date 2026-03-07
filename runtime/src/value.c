// QEntL运行时 - 值操作实现
// 版本: 1.0.0

#include "qentl_runtime.h"
#include <stdlib.h>
#include <string.h>
#include <stdio.h>
#include <math.h>

// ============================================================================
// 内部工具函数
// ============================================================================

static char* value_type_to_string(QentlType type) {
    switch (type) {
        case QENTL_TYPE_NULL:        return "null";
        case QENTL_TYPE_BOOLEAN:     return "boolean";
        case QENTL_TYPE_INTEGER:     return "integer";
        case QENTL_TYPE_FLOAT:       return "float";
        case QENTL_TYPE_STRING:      return "string";
        case QENTL_TYPE_ARRAY:       return "array";
        case QENTL_TYPE_OBJECT:      return "object";
        case QENTL_TYPE_FUNCTION:    return "function";
        default:                     return "unknown";
    }
}

static char* boolean_to_string(bool value) {
    return value ? qentl_string_create("true") : qentl_string_create("false");
}

static char* integer_to_string(int64_t value) {
    // 最大64位整数：-9223372036854775808，需要20字符 + 符号 + null
    char buffer[32];
    snprintf(buffer, sizeof(buffer), "%lld", (long long)value);
    return qentl_string_create(buffer);
}

static char* float_to_string(double value) {
    // 处理特殊值
    if (isnan(value)) {
        return qentl_string_create("NaN");
    }
    
    if (isinf(value)) {
        if (value > 0) {
            return qentl_string_create("Infinity");
        } else {
            return qentl_string_create("-Infinity");
        }
    }
    
    // 常规浮点数
    char buffer[64];
    snprintf(buffer, sizeof(buffer), "%.6g", value);
    
    // 确保有小数点
    if (strchr(buffer, '.') == NULL && strchr(buffer, 'e') == NULL && strchr(buffer, 'E') == NULL) {
        strcat(buffer, ".0");
    }
    
    return qentl_string_create(buffer);
}

static char* array_to_string(QentlArray* array) {
    if (array == NULL) {
        return qentl_string_create("[]");
    }
    
    size_t length = qentl_array_length(array);
    
    if (length == 0) {
        return qentl_string_create("[]");
    }
    
    // 开始构建字符串
    char* result = qentl_string_create("[");
    
    for (size_t i = 0; i < length; i++) {
        if (i > 0) {
            char* temp = qentl_string_concat(result, ", ");
            qentl_string_free(result);
            result = temp;
        }
        
        QentlValue element = qentl_array_get(array, i);
        char* element_str = qentl_value_to_string(element);
        
        char* temp = qentl_string_concat(result, element_str);
        qentl_string_free(result);
        qentl_string_free(element_str);
        result = temp;
    }
    
    char* temp = qentl_string_concat(result, "]");
    qentl_string_free(result);
    result = temp;
    
    return result;
}

// ============================================================================
// 公共API实现
// ============================================================================

QentlValue qentl_value_null(void) {
    QentlValue value;
    value.type = QENTL_TYPE_NULL;
    value.data.pointer = NULL;
    return value;
}

QentlValue qentl_value_boolean(bool value) {
    QentlValue result;
    result.type = QENTL_TYPE_BOOLEAN;
    result.data.boolean = value;
    return result;
}

QentlValue qentl_value_integer(int64_t value) {
    QentlValue result;
    result.type = QENTL_TYPE_INTEGER;
    result.data.integer = value;
    return result;
}

QentlValue qentl_value_float(double value) {
    QentlValue result;
    result.type = QENTL_TYPE_FLOAT;
    result.data.floating = value;
    return result;
}

QentlValue qentl_value_string(const char* value) {
    QentlValue result;
    result.type = QENTL_TYPE_STRING;
    
    if (value == NULL) {
        result.data.pointer = qentl_string_create("");
    } else {
        result.data.pointer = qentl_string_create(value);
    }
    
    return result;
}

QentlValue qentl_value_array(QentlArray* array) {
    QentlValue result;
    result.type = QENTL_TYPE_ARRAY;
    result.data.pointer = array;
    return result;
}

QentlType qentl_value_get_type(QentlValue value) {
    return value.type;
}

bool qentl_value_is_truthy(QentlValue value) {
    switch (value.type) {
        case QENTL_TYPE_NULL:
            return false;
            
        case QENTL_TYPE_BOOLEAN:
            return value.data.boolean;
            
        case QENTL_TYPE_INTEGER:
            return value.data.integer != 0;
            
        case QENTL_TYPE_FLOAT:
            return value.data.floating != 0.0;
            
        case QENTL_TYPE_STRING:
            if (value.data.pointer == NULL) {
                return false;
            }
            return strlen((char*)value.data.pointer) > 0;
            
        case QENTL_TYPE_ARRAY:
            if (value.data.pointer == NULL) {
                return false;
            }
            return qentl_array_length((QentlArray*)value.data.pointer) > 0;
            
        case QENTL_TYPE_OBJECT:
        case QENTL_TYPE_FUNCTION:
            return value.data.pointer != NULL;
            
        default:
            return false;
    }
}

QentlValue qentl_value_clone(QentlValue value) {
    switch (value.type) {
        case QENTL_TYPE_NULL:
        case QENTL_TYPE_BOOLEAN:
        case QENTL_TYPE_INTEGER:
        case QENTL_TYPE_FLOAT:
            // 基本类型直接复制
            return value;
            
        case QENTL_TYPE_STRING:
            if (value.data.pointer == NULL) {
                return qentl_value_string("");
            }
            return qentl_value_string((char*)value.data.pointer);
            
        case QENTL_TYPE_ARRAY:
            if (value.data.pointer == NULL) {
                return qentl_value_array(NULL);
            }
            
            // 深度克隆数组
            QentlArray* original = (QentlArray*)value.data.pointer;
            QentlArray* clone = qentl_array_create(qentl_array_capacity(original));
            
            if (clone == NULL) {
                return qentl_value_null();
            }
            
            size_t length = qentl_array_length(original);
            for (size_t i = 0; i < length; i++) {
                QentlValue element = qentl_array_get(original, i);
                QentlValue element_clone = qentl_value_clone(element);
                qentl_array_push(clone, element_clone);
            }
            
            return qentl_value_array(clone);
            
        case QENTL_TYPE_OBJECT:
        case QENTL_TYPE_FUNCTION:
            // 对象和函数：暂时不支持深度克隆，返回相同引用
            // TODO: 实现对象克隆
            return value;
            
        default:
            return qentl_value_null();
    }
}

void qentl_value_free(QentlValue value) {
    switch (value.type) {
        case QENTL_TYPE_STRING:
            if (value.data.pointer != NULL) {
                qentl_string_free((char*)value.data.pointer);
            }
            break;
            
        case QENTL_TYPE_ARRAY:
            if (value.data.pointer != NULL) {
                qentl_array_destroy((QentlArray*)value.data.pointer);
            }
            break;
            
        case QENTL_TYPE_OBJECT:
        case QENTL_TYPE_FUNCTION:
            // TODO: 实现对象和函数的释放
            if (value.data.pointer != NULL) {
                // 暂时只释放指针，不释放内容
                // qentl_free(value.data.pointer);
            }
            break;
            
        default:
            // 基本类型不需要特殊释放
            break;
    }
}

char* qentl_value_to_string(QentlValue value) {
    switch (value.type) {
        case QENTL_TYPE_NULL:
            return qentl_string_create("null");
            
        case QENTL_TYPE_BOOLEAN:
            return boolean_to_string(value.data.boolean);
            
        case QENTL_TYPE_INTEGER:
            return integer_to_string(value.data.integer);
            
        case QENTL_TYPE_FLOAT:
            return float_to_string(value.data.floating);
            
        case QENTL_TYPE_STRING:
            if (value.data.pointer == NULL) {
                return qentl_string_create("\"\"");
            }
            return qentl_string_format("\"%s\"", (char*)value.data.pointer);
            
        case QENTL_TYPE_ARRAY:
            return array_to_string((QentlArray*)value.data.pointer);
            
        case QENTL_TYPE_OBJECT:
            return qentl_string_format("[object:%p]", value.data.pointer);
            
        case QENTL_TYPE_FUNCTION:
            return qentl_string_format("[function:%p]", value.data.pointer);
            
        default:
            return qentl_string_format("[unknown:%d]", value.type);
    }
}

// ============================================================================
// 类型转换函数
// ============================================================================

QentlValue qentl_value_to_boolean(QentlValue value) {
    return qentl_value_boolean(qentl_value_is_truthy(value));
}

QentlValue qentl_value_to_integer(QentlValue value) {
    switch (value.type) {
        case QENTL_TYPE_NULL:
            return qentl_value_integer(0);
            
        case QENTL_TYPE_BOOLEAN:
            return qentl_value_integer(value.data.boolean ? 1 : 0);
            
        case QENTL_TYPE_INTEGER:
            return value;
            
        case QENTL_TYPE_FLOAT:
            return qentl_value_integer((int64_t)value.data.floating);
            
        case QENTL_TYPE_STRING:
            if (value.data.pointer == NULL) {
                return qentl_value_integer(0);
            }
            // 简单转换：尝试解析整数
            {
                char* endptr;
                int64_t int_value = strtoll((char*)value.data.pointer, &endptr, 10);
                if (endptr == (char*)value.data.pointer) {
                    // 转换失败
                    return qentl_value_integer(0);
                }
                return qentl_value_integer(int_value);
            }
            
        default:
            return qentl_value_integer(0);
    }
}

QentlValue qentl_value_to_float(QentlValue value) {
    switch (value.type) {
        case QENTL_TYPE_NULL:
            return qentl_value_float(0.0);
            
        case QENTL_TYPE_BOOLEAN:
            return qentl_value_float(value.data.boolean ? 1.0 : 0.0);
            
        case QENTL_TYPE_INTEGER:
            return qentl_value_float((double)value.data.integer);
            
        case QENTL_TYPE_FLOAT:
            return value;
            
        case QENTL_TYPE_STRING:
            if (value.data.pointer == NULL) {
                return qentl_value_float(0.0);
            }
            // 简单转换：尝试解析浮点数
            {
                char* endptr;
                double float_value = strtod((char*)value.data.pointer, &endptr);
                if (endptr == (char*)value.data.pointer) {
                    // 转换失败
                    return qentl_value_float(0.0);
                }
                return qentl_value_float(float_value);
            }
            
        default:
            return qentl_value_float(0.0);
    }
}

QentlValue qentl_value_to_string_value(QentlValue value) {
    char* str = qentl_value_to_string(value);
    QentlValue result = qentl_value_string(str);
    qentl_string_free(str);
    return result;
}

// ============================================================================
// 值比较函数
// ============================================================================

bool qentl_value_equals(QentlValue a, QentlValue b) {
    if (a.type != b.type) {
        // 类型不同，尝试类型转换后比较
        // 这里简化：只进行基本类型转换比较
        if ((a.type == QENTL_TYPE_INTEGER && b.type == QENTL_TYPE_FLOAT) ||
            (a.type == QENTL_TYPE_FLOAT && b.type == QENTL_TYPE_INTEGER)) {
            // 整数和浮点数比较
            double a_float = (a.type == QENTL_TYPE_INTEGER) ? 
                            (double)a.data.integer : a.data.floating;
            double b_float = (b.type == QENTL_TYPE_INTEGER) ? 
                            (double)b.data.integer : b.data.floating;
            return a_float == b_float;
        }
        return false;
    }
    
    // 相同类型比较
    switch (a.type) {
        case QENTL_TYPE_NULL:
            return true; // 所有null相等
            
        case QENTL_TYPE_BOOLEAN:
            return a.data.boolean == b.data.boolean;
            
        case QENTL_TYPE_INTEGER:
            return a.data.integer == b.data.integer;
            
        case QENTL_TYPE_FLOAT:
            return a.data.floating == b.data.floating;
            
        case QENTL_TYPE_STRING:
            if (a.data.pointer == NULL && b.data.pointer == NULL) {
                return true;
            }
            if (a.data.pointer == NULL || b.data.pointer == NULL) {
                return false;
            }
            return strcmp((char*)a.data.pointer, (char*)b.data.pointer) == 0;
            
        case QENTL_TYPE_ARRAY:
        case QENTL_TYPE_OBJECT:
        case QENTL_TYPE_FUNCTION:
            // 引用相等
            return a.data.pointer == b.data.pointer;
            
        default:
            return false;
    }
}

int qentl_value_compare(QentlValue a, QentlValue b) {
    // 首先尝试作为数字比较
    QentlValue a_num = qentl_value_to_float(a);
    QentlValue b_num = qentl_value_to_float(b);
    
    if (a_num.type == QENTL_TYPE_FLOAT && b_num.type == QENTL_TYPE_FLOAT) {
        double a_val = a_num.data.floating;
        double b_val = b_num.data.floating;
        
        if (a_val < b_val) return -1;
        if (a_val > b_val) return 1;
        return 0;
    }
    
    // 否则作为字符串比较
    char* a_str = qentl_value_to_string(a);
    char* b_str = qentl_value_to_string(b);
    
    int result = strcmp(a_str, b_str);
    
    qentl_string_free(a_str);
    qentl_string_free(b_str);
    
    return result;
}

// ============================================================================
// 调试函数
// ============================================================================

void qentl_value_dump(QentlValue value) {
    char* type_str = value_type_to_string(value.type);
    char* value_str = qentl_value_to_string(value);
    
    printf("[值] type=%s, value=%s\n", type_str, value_str);
    
    qentl_string_free(value_str);
}