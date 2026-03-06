// QEntL运行时 - 字符串操作实现
// 版本: 1.0.0

#include "qentl_runtime.h"
#include <stdlib.h>
#include <string.h>
#include <stdarg.h>
#include <stdio.h>
#include <ctype.h>

// ============================================================================
// 内部工具函数
// ============================================================================

static size_t string_calculate_length(const char* str) {
    if (str == NULL) {
        return 0;
    }
    
    // 检查是否包含中文字符，正确计算长度
    size_t len = 0;
    while (*str) {
        // 检查UTF-8多字节字符
        unsigned char c = (unsigned char)*str;
        if ((c & 0x80) == 0) {
            // ASCII字符
            str++;
        } else if ((c & 0xE0) == 0xC0) {
            // 2字节UTF-8
            str += 2;
        } else if ((c & 0xF0) == 0xE0) {
            // 3字节UTF-8
            str += 3;
        } else if ((c & 0xF8) == 0xF0) {
            // 4字节UTF-8
            str += 4;
        } else {
            // 无效UTF-8，当作单字节处理
            str++;
        }
        len++;
    }
    
    return len;
}

// ============================================================================
// 公共API实现
// ============================================================================

char* qentl_string_create(const char* value) {
    if (value == NULL) {
        // 返回空字符串而不是NULL
        char* str = (char*)qentl_alloc(1);
        if (str != NULL) {
            str[0] = '\0';
        }
        return str;
    }
    
    size_t len = strlen(value);
    char* str = (char*)qentl_alloc(len + 1);
    
    if (str != NULL) {
        memcpy(str, value, len);
        str[len] = '\0';
    }
    
    return str;
}

char* qentl_string_create_const(const char* value) {
    // 注意：这个函数不复制字符串，调用者必须确保value的生命周期
    // 主要用于常量字符串，减少分配开销
    return (char*)value;
}

char* qentl_string_concat(const char* str1, const char* str2) {
    if (str1 == NULL && str2 == NULL) {
        return qentl_string_create("");
    }
    
    if (str1 == NULL) {
        return qentl_string_create(str2);
    }
    
    if (str2 == NULL) {
        return qentl_string_create(str1);
    }
    
    size_t len1 = strlen(str1);
    size_t len2 = strlen(str2);
    size_t total_len = len1 + len2;
    
    char* result = (char*)qentl_alloc(total_len + 1);
    
    if (result != NULL) {
        memcpy(result, str1, len1);
        memcpy(result + len1, str2, len2);
        result[total_len] = '\0';
    }
    
    return result;
}

char* qentl_string_format(const char* format, ...) {
    if (format == NULL) {
        return qentl_string_create("");
    }
    
    // 第一次调用：计算所需缓冲区大小
    va_list args;
    va_start(args, format);
    int needed_size = vsnprintf(NULL, 0, format, args);
    va_end(args);
    
    if (needed_size < 0) {
        // 格式化错误
        return qentl_string_create("[格式化错误]");
    }
    
    // 分配缓冲区
    char* buffer = (char*)qentl_alloc(needed_size + 1);
    if (buffer == NULL) {
        return qentl_string_create("[内存分配失败]");
    }
    
    // 第二次调用：实际格式化
    va_start(args, format);
    vsnprintf(buffer, needed_size + 1, format, args);
    va_end(args);
    
    return buffer;
}

size_t qentl_string_length(const char* str) {
    if (str == NULL) {
        return 0;
    }
    return string_calculate_length(str);
}

void qentl_string_free(char* str) {
    if (str != NULL) {
        qentl_free(str);
    }
}

// ============================================================================
// 工具函数实现
// ============================================================================

bool qentl_string_is_empty(const char* str) {
    if (str == NULL) {
        return true;
    }
    
    // 跳过空白字符
    while (*str) {
        if (!isspace((unsigned char)*str)) {
            return false;
        }
        str++;
    }
    
    return true;
}

bool qentl_char_is_letter(char c) {
    // 检查英文
    if ((c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z')) {
        return true;
    }
    
    // 检查中文（基本汉字区）
    // 注意：这里简化处理，实际上需要检查UTF-8编码
    // 对于简单实现，我们假设非ASCII字符可能是中文
    if ((unsigned char)c >= 0x80) {
        return true;
    }
    
    return false;
}

bool qentl_char_is_digit(char c) {
    return c >= '0' && c <= '9';
}

bool qentl_char_is_alnum(char c) {
    return qentl_char_is_letter(c) || qentl_char_is_digit(c) || c == '_';
}

char qentl_char_tolower(char c) {
    if (c >= 'A' && c <= 'Z') {
        return c + ('a' - 'A');
    }
    return c;
}

int qentl_string_compare(const char* str1, const char* str2) {
    if (str1 == NULL && str2 == NULL) {
        return 0;
    }
    
    if (str1 == NULL) {
        return -1;
    }
    
    if (str2 == NULL) {
        return 1;
    }
    
    return strcmp(str1, str2);
}

char* qentl_string_copy(const char* str) {
    return qentl_string_create(str);
}

// ============================================================================
// 扩展字符串操作
// ============================================================================

char* qentl_string_substring(const char* str, size_t start, size_t length) {
    if (str == NULL || str[0] == '\0') {
        return qentl_string_create("");
    }
    
    size_t str_len = strlen(str);
    
    // 检查边界
    if (start >= str_len) {
        return qentl_string_create("");
    }
    
    if (start + length > str_len) {
        length = str_len - start;
    }
    
    char* result = (char*)qentl_alloc(length + 1);
    if (result != NULL) {
        memcpy(result, str + start, length);
        result[length] = '\0';
    }
    
    return result;
}

char* qentl_string_trim(const char* str) {
    if (str == NULL || str[0] == '\0') {
        return qentl_string_create("");
    }
    
    // 找到起始位置（跳过前导空白）
    const char* start = str;
    while (*start && isspace((unsigned char)*start)) {
        start++;
    }
    
    // 全部是空白
    if (*start == '\0') {
        return qentl_string_create("");
    }
    
    // 找到结束位置
    const char* end = str + strlen(str) - 1;
    while (end > start && isspace((unsigned char)*end)) {
        end--;
    }
    
    size_t len = end - start + 1;
    char* result = (char*)qentl_alloc(len + 1);
    
    if (result != NULL) {
        memcpy(result, start, len);
        result[len] = '\0';
    }
    
    return result;
}

bool qentl_string_starts_with(const char* str, const char* prefix) {
    if (str == NULL || prefix == NULL) {
        return false;
    }
    
    size_t str_len = strlen(str);
    size_t prefix_len = strlen(prefix);
    
    if (prefix_len > str_len) {
        return false;
    }
    
    return strncmp(str, prefix, prefix_len) == 0;
}

bool qentl_string_ends_with(const char* str, const char* suffix) {
    if (str == NULL || suffix == NULL) {
        return false;
    }
    
    size_t str_len = strlen(str);
    size_t suffix_len = strlen(suffix);
    
    if (suffix_len > str_len) {
        return false;
    }
    
    return strcmp(str + str_len - suffix_len, suffix) == 0;
}

char* qentl_string_replace(const char* str, const char* old, const char* new) {
    if (str == NULL || old == NULL || new == NULL) {
        return qentl_string_create(str);
    }
    
    if (str[0] == '\0' || old[0] == '\0') {
        return qentl_string_create(str);
    }
    
    // 计算出现次数
    size_t count = 0;
    const char* pos = str;
    size_t old_len = strlen(old);
    
    while ((pos = strstr(pos, old)) != NULL) {
        count++;
        pos += old_len;
    }
    
    if (count == 0) {
        return qentl_string_create(str);
    }
    
    // 计算新字符串长度
    size_t str_len = strlen(str);
    size_t new_len = strlen(new);
    size_t result_len = str_len + count * (new_len - old_len);
    
    // 分配结果缓冲区
    char* result = (char*)qentl_alloc(result_len + 1);
    if (result == NULL) {
        return qentl_string_create(str);
    }
    
    // 执行替换
    char* dest = result;
    const char* src = str;
    
    while (*src) {
        if (strstr(src, old) == src) {
            memcpy(dest, new, new_len);
            dest += new_len;
            src += old_len;
        } else {
            *dest++ = *src++;
        }
    }
    
    *dest = '\0';
    return result;
}