# QEntL编译器模块CMake构建文件

# 设置最低CMake版本
cmake_minimum_required(VERSION 3.10)

# 添加编译器源文件
set(COMPILER_SOURCES
    qentl_compiler.c
    lexer.c
    parser.c
    ast.c
    semantic_analyzer.c
    code_generator.c
    optimizer.c
    symbol_table.c
    error_handler.c
)

# 添加编译器头文件
set(COMPILER_HEADERS
    qentl_compiler.h
    lexer.h
    parser.h
    ast.h
    semantic_analyzer.h
    code_generator.h
    optimizer.h
    symbol_table.h
    error_handler.h
)

# 创建编译器库
add_library(qentl_compiler STATIC ${COMPILER_SOURCES} ${COMPILER_HEADERS})

# 设置包含目录
target_include_directories(qentl_compiler PUBLIC
    ${CMAKE_CURRENT_SOURCE_DIR}
    ${CMAKE_SOURCE_DIR}/src
)

# 设置编译选项
target_compile_options(qentl_compiler PRIVATE
    -Wall
    -Wextra
    -pedantic
    -std=c99
)

# 如果是调试模式，添加调试符号和禁用优化
if(CMAKE_BUILD_TYPE STREQUAL "Debug")
    target_compile_options(qentl_compiler PRIVATE
        -g
        -O0
    )
endif()

# 设置链接库
target_link_libraries(qentl_compiler
    m  # 数学库
) 