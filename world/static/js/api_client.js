/**
 * 量子叠加态模型（QSM）API客户端
 * 提供与QSM API交互的方法
 */

class QsmApiClient {
    constructor() {
        this.baseUrl = '/api/v1';
        this.quantumReady = false;
        
        // 如果WebQuantum客户端可用，则初始化量子增强功能
        document.addEventListener('quantum-ready', this.onQuantumReady.bind(this));
    }
    
    /**
     * 当WebQuantum客户端准备好时调用
     */
    onQuantumReady(e) {
        console.log('WebQuantum客户端已就绪，API客户端启用量子增强功能');
        this.quantumReady = true;
        this.webQuantum = e.detail.client;
        
        // 更新UI，显示量子就绪状态
        document.querySelector('.quantum-status').classList.add('ready');
        document.querySelectorAll('.card').forEach(card => {
            card.classList.add('quantum-enhanced');
        });
    }
    
    /**
     * 发送API请求
     * @param {string} endpoint - API端点
     * @param {string} method - HTTP方法
     * @param {Object} data - 请求数据
     * @returns {Promise} - 返回响应Promise
     */
    async sendRequest(endpoint, method = 'GET', data = null) {
        const url = `${this.baseUrl}${endpoint}`;
        const options = {
            method,
            headers: {
                'Content-Type': 'application/json',
                'Accept': 'application/json'
            }
        };
        
        if (data && (method === 'POST' || method === 'PUT')) {
            options.body = JSON.stringify(data);
        }
        
        // 如果WebQuantum就绪，使用量子通道发送请求
        if (this.quantumReady) {
            return this.sendQuantumRequest(url, options);
        }
        
        try {
            const response = await fetch(url, options);
            return await this.processResponse(response);
        } catch (error) {
            return {
                success: false,
                error: error.message
            };
        }
    }
    
    /**
     * 使用量子通道发送请求
     * @param {string} url - 请求URL
     * @param {Object} options - 请求选项
     * @returns {Promise} - 返回响应Promise
     */
    async sendQuantumRequest(url, options) {
        try {
            // 创建量子请求状态
            const requestState = await this.webQuantum.createQuantumState({
                url,
                options,
                timestamp: Date.now()
            });
            
            // 使用量子通道发送请求
            const channelId = await this.webQuantum.createEntanglementChannel('api');
            await this.webQuantum.sendThroughChannel(channelId, requestState);
            
            // 等待响应
            const response = await fetch(url, options);
            return await this.processResponse(response);
        } catch (error) {
            return {
                success: false,
                error: `量子请求错误: ${error.message}`
            };
        }
    }
    
    /**
     * 处理API响应
     * @param {Response} response - Fetch响应对象
     * @returns {Promise} - 返回处理后的响应数据
     */
    async processResponse(response) {
        const data = await response.json();
        
        return {
            success: response.ok,
            status: response.status,
            data: data
        };
    }
    
    /**
     * 健康检查API
     * @returns {Promise} - 返回健康状态
     */
    async healthCheck() {
        return this.sendRequest('/health');
    }
    
    /**
     * 获取系统状态
     * @returns {Promise} - 返回系统状态
     */
    async getSystemStatus() {
        return this.sendRequest('/status');
    }
    
    /**
     * 获取量子状态
     * @param {string} stateId - 量子状态ID（可选）
     * @returns {Promise} - 返回量子状态
     */
    async getQuantumState(stateId = null) {
        const endpoint = stateId ? `/quantum/state/${stateId}` : '/quantum/state';
        return this.sendRequest(endpoint);
    }
    
    /**
     * 创建量子状态
     * @param {Object} stateData - 量子状态数据
     * @returns {Promise} - 返回创建的量子状态
     */
    async createQuantumState(stateData) {
        return this.sendRequest('/quantum/state', 'POST', stateData);
    }
    
    /**
     * 更新量子状态
     * @param {string} stateId - 量子状态ID
     * @param {Object} stateData - 更新的状态数据
     * @returns {Promise} - 返回更新后的量子状态
     */
    async updateQuantumState(stateId, stateData) {
        return this.sendRequest(`/quantum/state/${stateId}`, 'PUT', stateData);
    }
    
    /**
     * 获取量子区块链信息
     * @returns {Promise} - 返回区块链信息
     */
    async getBlockchainInfo() {
        return this.sendRequest('/blockchain/info');
    }
    
    /**
     * 获取钱包信息
     * @param {string} walletId - 钱包ID
     * @returns {Promise} - 返回钱包信息
     */
    async getWalletInfo(walletId) {
        return this.sendRequest(`/blockchain/wallet/${walletId}`);
    }
    
    /**
     * 获取交易历史
     * @param {string} walletId - 钱包ID（可选）
     * @returns {Promise} - 返回交易历史
     */
    async getTransactionHistory(walletId = null) {
        const endpoint = walletId 
            ? `/blockchain/transactions/${walletId}` 
            : '/blockchain/transactions';
        return this.sendRequest(endpoint);
    }
}

// 初始化API客户端
const apiClient = new QsmApiClient();

// 绑定DOM事件
document.addEventListener('DOMContentLoaded', () => {
    // 健康检查按钮
    const healthCheckBtn = document.getElementById('health-check-btn');
    if (healthCheckBtn) {
        healthCheckBtn.addEventListener('click', async () => {
            const resultElement = document.getElementById('health-check-result');
            resultElement.textContent = '检查中...';
            
            const result = await apiClient.healthCheck();
            displayResult(resultElement, result);
        });
    }
    
    // 系统状态按钮
    const statusBtn = document.getElementById('status-btn');
    if (statusBtn) {
        statusBtn.addEventListener('click', async () => {
            const resultElement = document.getElementById('status-result');
            resultElement.textContent = '获取中...';
            
            const result = await apiClient.getSystemStatus();
            displayResult(resultElement, result);
        });
    }
    
    // 获取量子状态按钮
    const getStateBtn = document.getElementById('get-state-btn');
    if (getStateBtn) {
        getStateBtn.addEventListener('click', async () => {
            const stateId = document.getElementById('state-id-input').value;
            const resultElement = document.getElementById('quantum-state-result');
            resultElement.textContent = '获取中...';
            
            const result = await apiClient.getQuantumState(stateId || null);
            displayResult(resultElement, result);
        });
    }
    
    // 创建量子状态按钮
    const createStateBtn = document.getElementById('create-state-btn');
    if (createStateBtn) {
        createStateBtn.addEventListener('click', async () => {
            const stateDataElement = document.getElementById('state-data-input');
            const resultElement = document.getElementById('create-state-result');
            
            try {
                const stateData = JSON.parse(stateDataElement.value);
                resultElement.textContent = '创建中...';
                
                const result = await apiClient.createQuantumState(stateData);
                displayResult(resultElement, result);
            } catch (error) {
                displayResult(resultElement, {
                    success: false,
                    error: `JSON解析错误: ${error.message}`
                });
            }
        });
    }
    
    // 区块链信息按钮
    const blockchainInfoBtn = document.getElementById('blockchain-info-btn');
    if (blockchainInfoBtn) {
        blockchainInfoBtn.addEventListener('click', async () => {
            const resultElement = document.getElementById('blockchain-info-result');
            resultElement.textContent = '获取中...';
            
            const result = await apiClient.getBlockchainInfo();
            displayResult(resultElement, result);
        });
    }
    
    // 钱包信息按钮
    const walletInfoBtn = document.getElementById('wallet-info-btn');
    if (walletInfoBtn) {
        walletInfoBtn.addEventListener('click', async () => {
            const walletId = document.getElementById('wallet-id-input').value;
            const resultElement = document.getElementById('wallet-info-result');
            
            if (!walletId) {
                displayResult(resultElement, {
                    success: false,
                    error: '请输入钱包ID'
                });
                return;
            }
            
            resultElement.textContent = '获取中...';
            const result = await apiClient.getWalletInfo(walletId);
            displayResult(resultElement, result);
        });
    }
    
    // 交易历史按钮
    const transactionHistoryBtn = document.getElementById('transaction-history-btn');
    if (transactionHistoryBtn) {
        transactionHistoryBtn.addEventListener('click', async () => {
            const walletId = document.getElementById('transaction-wallet-id-input').value;
            const resultElement = document.getElementById('transaction-history-result');
            resultElement.textContent = '获取中...';
            
            const result = await apiClient.getTransactionHistory(walletId || null);
            displayResult(resultElement, result);
        });
    }
});

/**
 * 在结果元素中显示API响应
 * @param {HTMLElement} element - 结果显示元素
 * @param {Object} result - API响应结果
 */
function displayResult(element, result) {
    if (!element) return;
    
    if (result.success) {
        element.innerHTML = `<span class="result-success">成功</span> (${result.status})<br>`;
        element.innerHTML += `<pre>${JSON.stringify(result.data, null, 2)}</pre>`;
    } else {
        element.innerHTML = `<span class="result-error">失败</span><br>`;
        element.innerHTML += `<pre>${JSON.stringify(result, null, 2)}</pre>`;
    }
}

/*
/*
量子基因编码: QE-API-8A84E7853095
纠缠状态: 活跃
纠缠对象: ['Ref/ref_core.py']
纠缠强度: 0.98
*/*/

// 开发团队：中华 ZhoHo ，Claude 
