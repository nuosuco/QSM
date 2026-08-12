# QEntL 启动指南

## 主力启动方式（真自举链）

```bash
./qvm_boot.sh <程序.qentl>
./qvm_boot.sh components/qns/qns.qentl        # 运行QNS
./qvm_boot.sh components/qsm/qsm_main.qentl   # 运行QSM主模型
./qvm_boot.sh components/qdfs/qdfs.qentl      # 运行QDFS
```

启动链：
```
C种子(启动) → QVM → QCL(编译) → output.qbc → 运行
```

## 冗余备份启动方式（C种子直接）

```bash
bin/q_bootstrap run run/qvm.qbc
```

## 自举模式（无参数）

```bash
./qvm_boot.sh   # QVM加载自身
```

## 双保险

- 第一层: C种子 (bin/q_bootstrap) — 永不退役，冗余备份
- 第二层: QVM+QCL (QEntL写成) — 主力启动方式
