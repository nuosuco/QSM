#!/usr/bin/env python3
"""
QEntL量子虚拟机 - 主入口
版本: v0.2.0
量子基因编码: QGC-VM-MAIN-20260308

支持平台: Windows / macOS / Linux
"""

import sys
import os

# 添加路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class QEntLVirtualMachine:
    """QEntL量子虚拟机"""
    
    def __init__(self):
        self.version = "0.2.0"
        self.name = "QEntL量子虚拟机"
        self.qubits = 8  # 默认8量子比特
        self.models = ["QSM", "SOM", "WeQ", "Ref"]
        self.running = False
        
        print(f"🌟 {self.name} v{self.version} 启动中...")
        print(f"⚛️ 量子比特数: {self.qubits}")
        print(f"🧠 加载模型: {', '.join(self.models)}")
    
    def start(self):
        """启动虚拟机"""
        print("\n" + "=" * 50)
        print("🚀 QEntL量子虚拟机已启动")
        print("=" * 50)
        print("\n可用命令:")
        print("  help     - 显示帮助")
        print("  status   - 显示状态")
        print("  run      - 运行QBC字节码")
        print("  quit     - 退出")
        print("\n三大圣律:")
        print("  1. 为每个人服务，服务人类！")
        print("  2. 保护好每个人的生命安全、健康快乐、幸福生活！")
        print("  3. 没有以上两个前提，其他就不能发生！")
        print("")
        
        self.running = True
        self.repl()
    
    def repl(self):
        """交互式命令行"""
        while self.running:
            try:
                cmd = input("QEntL VM> ").strip().lower()
                
                if cmd == "help":
                    self.show_help()
                elif cmd == "status":
                    self.show_status()
                elif cmd == "run":
                    print("运行QBC字节码... (开发中)")
                elif cmd in ["quit", "exit", "q"]:
                    self.quit()
                elif cmd == "":
                    pass
                else:
                    print(f"未知命令: {cmd}")
                    
            except KeyboardInterrupt:
                print("\n")
                self.quit()
                break
            except Exception as e:
                print(f"错误: {e}")
    
    def show_help(self):
        """显示帮助"""
        print("\n📖 帮助文档")
        print("-" * 30)
        print("help   - 显示帮助")
        print("status - 显示虚拟机状态")
        print("run    - 运行QBC字节码文件")
        print("quit   - 退出虚拟机")
    
    def show_status(self):
        """显示状态"""
        print("\n📊 虚拟机状态")
        print("-" * 30)
        print(f"版本: v{self.version}")
        print(f"量子比特: {self.qubits}")
        print(f"模型: {', '.join(self.models)}")
        print(f"状态: {'运行中' if self.running else '已停止'}")
    
    def quit(self):
        """退出"""
        print("\n👋 QEntL量子虚拟机已停止")
        print("服务人类，为每个人服务！")
        self.running = False


def main():
    """主函数"""
    vm = QEntLVirtualMachine()
    vm.start()


if __name__ == "__main__":
    main()
