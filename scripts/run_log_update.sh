#!/bin/bash
#
# 日志路径更新工具启动脚本
# 此脚本用于测试和运行日志路径更新工具

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# 状态输出函数
function print_status() {
    echo -e "${CYAN}[STATUS] $1${NC}"
}

function print_warning() {
    echo -e "${YELLOW}[WARNING] $1${NC}"
}

function print_error() {
    echo -e "${RED}[ERROR] $1${NC}"
}

function print_success() {
    echo -e "${GREEN}[SUCCESS] $1${NC}"
}

# 确保.logs目录存在
logs_dir=".logs"
if [ ! -d "$logs_dir" ]; then
    mkdir -p "$logs_dir"
    print_success "Created .logs directory at $(realpath $logs_dir)"
fi

# 确保scripts/test_cases目录存在
test_cases_dir="scripts/test_cases"
if [ ! -d "$test_cases_dir" ]; then
    mkdir -p "$test_cases_dir"
    print_status "Created test cases directory at $(realpath $test_cases_dir)"
fi

# 检查测试用例是否存在
test_case="$test_cases_dir/test_log_paths.py"
if [ ! -f "$test_case" ]; then
    print_warning "Test case file not found at $test_case"
else
    print_status "Test case file found at $test_case"
fi

# 检查更新脚本是否存在
update_script="scripts/update_log_paths.py"
if [ ! -f "$update_script" ]; then
    print_error "Update script not found at $update_script"
    exit 1
fi

print_status "Starting log path update process..."

# 处理命令行参数
run_test=false
dry_run=false
restore=false
verbose=false
add_log_config=false
exclude_patterns=()

# 解析命令行参数
i=0
while [ $i -lt $# ]; do
    case "${!i}" in
        --test)
            run_test=true
            ;;
        --dry-run)
            dry_run=true
            ;;
        --restore)
            restore=true
            ;;
        --verbose)
            verbose=true
            ;;
        --add-log-config)
            add_log_config=true
            ;;
        --exclude)
            i=$((i+1))
            # 收集所有在--exclude后面且不是以--开头的参数
            while [ $i -lt $# ] && [[ ! "${!i}" =~ ^-- ]]; do
                exclude_patterns+=("${!i}")
                i=$((i+1))
            done
            i=$((i-1))  # 回退一个位置，因为最后一个参数会在下一次循环中被处理
            ;;
    esac
    i=$((i+1))
done

# 构建命令行参数
cmd_args=()
if [ "$dry_run" = true ]; then
    cmd_args+=("--dry-run")
fi
if [ "$verbose" = true ]; then
    cmd_args+=("--verbose")
fi
if [ "$add_log_config" = true ]; then
    cmd_args+=("--add-log-config")
fi
if [ ${#exclude_patterns[@]} -gt 0 ]; then
    cmd_args+=("--exclude")
    for pattern in "${exclude_patterns[@]}"; do
        cmd_args+=("$pattern")
    done
fi

# 如果传入了--test参数，则只运行测试用例
if [ "$run_test" = true ]; then
    print_status "Running in test mode..."
    
    # 运行更新脚本，只处理测试目录
    cmd_args+=("$test_cases_dir")
    print_status "Command: python3 $update_script ${cmd_args[*]}"
    python3 "$update_script" "${cmd_args[@]}"
    
    # 检查测试用例文件更新后的结果
    print_status "Test completed. Please check the update results in $test_case"
    
    # 展示更新后的文件内容
    print_status "Updated test case content:"
    while IFS= read -r line; do
        if [[ $line == *"os.path.join"* ]]; then
            echo -e "${GREEN}$line${NC}"
        else
            echo "$line"
        fi
    done < "$test_case"
else
    # 如果是干运行模式，不需要确认
    if [ "$dry_run" = false ]; then
        # 询问用户确认是否运行完整更新
        read -p "This will update log paths in all Python files in the project. Continue? (y/n) " confirmation
        if [ "$confirmation" != "y" ]; then
            print_warning "Operation cancelled by user."
            exit 0
        fi
    else
        print_status "Running in dry-run mode - no files will be modified."
    fi
    
    # 运行更新脚本，处理整个项目
    cmd_args+=(".")
    print_status "Command: python3 $update_script ${cmd_args[*]}"
    python3 "$update_script" "${cmd_args[@]}"
    
    if [ "$dry_run" = true ]; then
        print_success "Dry run completed. Check the log file at .logs/update_log_paths.log for details."
    else
        print_success "Log path update completed. Check the log file at .logs/update_log_paths.log for details."
    fi
fi

# 如果传入了--restore参数，则还原测试用例文件
if [ "$restore" = true ]; then
    print_status "Restoring test case file to original state..."
    
    # 这里可以实现还原测试用例的逻辑，如果需要的话
    # 例如，可以保存一个备份，或者重新生成测试用例文件
    
    print_status "Test case file restored."
fi

print_status "Done!" 
#
量子基因编码: QE-RUN-18A3B3112A8B
纠缠状态: 活跃
纠缠对象: ['Ref/ref_core.py']
纠缠强度: 0.98
