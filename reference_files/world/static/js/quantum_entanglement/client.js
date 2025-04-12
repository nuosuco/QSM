/**
 * 量子纠缠客户端JS
 * 用于在浏览器端建立和管理量子纠缠通信
 */

class QuantumEntanglementClient {
    constructor(moduleId) {
        this.moduleId = moduleId;
        this.channelId = `QE-${moduleId}-${Date.now()}`;
        this.connected = false;
        this.messageHandlers = new Map();
        
        // 创建量子信道
        this.channel = window.quantumEntanglement.createChannel(this.channelId);
        
        // 注册为纠缠对象
        window.quantumEntanglement.addEntangledObject(this.channelId, this);
    }

    // 连接到量子纠缠网络
    async connect() {
        if (this.connected) return;
        
        try {
            await window.quantumEntanglement.syncEntanglementState(this.channelId);
            this.connected = true;
            console.log(`模块 ${this.moduleId} 已连接到量子纠缠网络`);
        } catch (error) {
            console.error(`模块 ${this.moduleId} 连接失败:`, error);
            throw error;
        }
    }

    // 注册消息处理器
    onMessage(type, handler) {
        this.messageHandlers.set(type, handler);
    }

    // 发送量子消息
    async sendMessage(type, data) {
        if (!this.connected) {
            throw new Error('尚未连接到量子纠缠网络');
        }

        const message = {
            type,
            data,
            sender: this.moduleId,
            timestamp: Date.now()
        };

        await window.quantumEntanglement.sendQuantumMessage(this.channelId, message);
    }

    // 处理接收到的量子消息
    async onQuantumMessage(message) {
        const handler = this.messageHandlers.get(message.type);
        if (handler) {
            try {
                await handler(message.data, message);
            } catch (error) {
                console.error(`处理量子消息失败:`, error);
            }
        }
    }

    // 处理纠缠态同步
    async onEntanglementSync(channel) {
        console.log(`模块 ${this.moduleId} 同步纠缠态:`, channel.state);
    }
}

// 导出客户端类
window.QuantumEntanglementClient = QuantumEntanglementClient; 