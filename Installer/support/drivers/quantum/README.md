# Quantum Hardware Drivers
# 量子硬件驱动程序

## 支持的量子硬件

### IBM Quantum
- IBM Quantum Experience
- IBM Quantum Network
- Qiskit Runtime Service

### Google Quantum AI
- Cirq Quantum Computing Framework  
- Quantum AI Processor
- TensorFlow Quantum

### IonQ
- IonQ Quantum Computer
- IonQ Quantum Cloud Service

### Microsoft Azure Quantum
- Azure Quantum Service
- Q# Quantum Development Kit

## 驱动安装

量子硬件驱动会在QEntL系统安装时自动安装。
如需手动安装，请运行:

```bash
qentl-driver install quantum --provider=ibm
qentl-driver install quantum --provider=google  
qentl-driver install quantum --provider=ionq
qentl-driver install quantum --provider=microsoft
```

## 配置量子硬件

安装完成后，需要配置量子硬件连接:

```bash
qentl-config quantum --provider=ibm --token=YOUR_IBM_TOKEN
qentl-config quantum --provider=google --credentials=path/to/credentials.json
```
