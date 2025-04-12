/**
 * 量子纠缠通信核心JS
 * 提供跨模块的量子纠缠通信功能
 */

class QuantumEntanglement {
    constructor() {
        this.entanglementState = 'ACTIVE';
        this.entangledObjects = new Set();
        this.entanglementStrength = 1.0;
        this.quantumChannels = new Map();
    }

    // 创建量子纠缠信道
    createChannel(channelId, options = {}) {
        const channel = {
            id: channelId,
            state: 'READY',
            strength: options.strength || 1.0,
            objects: new Set(),
            lastSync: Date.now()
        };
        
        this.quantumChannels.set(channelId, channel);
        return channel;
    }

    // 添加纠缠对象
    addEntangledObject(channelId, object) {
        const channel = this.quantumChannels.get(channelId);
        if (!channel) {
            throw new Error(`量子信道 ${channelId} 不存在`);
        }
        
        channel.objects.add(object);
        this.entangledObjects.add(object);
    }

    // 同步纠缠态
    async syncEntanglementState(channelId) {
        const channel = this.quantumChannels.get(channelId);
        if (!channel) return;

        channel.lastSync = Date.now();
        channel.state = 'SYNCING';

        try {
            // 向所有纠缠对象广播状态
            for (const obj of channel.objects) {
                if (typeof obj.onEntanglementSync === 'function') {
                    await obj.onEntanglementSync(channel);
                }
            }
            
            channel.state = 'READY';
        } catch (error) {
            console.error('量子纠缠同步失败:', error);
            channel.state = 'ERROR';
        }
    }

    // 发送量子消息
    async sendQuantumMessage(channelId, message) {
        const channel = this.quantumChannels.get(channelId);
        if (!channel) {
            throw new Error(`量子信道 ${channelId} 不存在`);
        }

        // 添加量子基因编码
        message.quantumGene = 'QG-MSG-' + Math.random().toString(36).substr(2, 9);
        
        // 广播消息到所有纠缠对象
        const promises = Array.from(channel.objects).map(obj => {
            if (typeof obj.onQuantumMessage === 'function') {
                return obj.onQuantumMessage(message);
            }
        });

        await Promise.all(promises);
    }
}

// 创建全局量子纠缠实例
window.quantumEntanglement = new QuantumEntanglement(); 