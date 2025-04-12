/**
 * QSM核心JavaScript文件
 * 提供量子叠加态模型的基础功能
 */

// 在DOMContentLoaded事件中初始化
document.addEventListener('DOMContentLoaded', function() {
  console.log('QSM Core 加载完成');
  
  // 初始化量子叠加态组件
  initQuantumComponents();
  
  // 初始化特定页面功能
  initPageSpecificFeatures();
});

/**
 * 初始化量子叠加态组件
 */
function initQuantumComponents() {
  // 初始化量子效果
  initQuantumEffects();
  
  // 初始化量子测试功能（如果存在）
  if (document.querySelector('.quantum-test-container')) {
    initQuantumTest();
  }
  
  // 初始化量子体验功能（如果存在）
  if (document.querySelector('.quantum-experience')) {
    initQuantumExperience();
  }
  
  // 初始化API客户端（如果存在）
  if (document.querySelector('.api-client-container')) {
    initApiClient();
  }
}

/**
 * 初始化量子效果
 */
function initQuantumEffects() {
  // 为带有quantum-effect类的元素添加鼠标悬停效果
  const quantumElements = document.querySelectorAll('.quantum-effect');
  
  quantumElements.forEach(element => {
    element.addEventListener('mousemove', function(e) {
      const rect = element.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;
      
      // 创建光晕效果
      element.style.setProperty('--x', `${x}px`);
      element.style.setProperty('--y', `${y}px`);
    });
  });
}

/**
 * 初始化页面特定功能
 */
function initPageSpecificFeatures() {
  // 获取当前页面路径
  const path = window.location.pathname;
  
  // 根据路径初始化特定功能
  if (path.includes('/quantum_test')) {
    initQuantumTest();
  } else if (path.includes('/quantum_experience')) {
    initQuantumExperience();
  } else if (path.includes('/api_client')) {
    initApiClient();
  }
}

/**
 * 初始化量子测试功能
 */
function initQuantumTest() {
  const container = document.querySelector('.quantum-test-container');
  if (!container) return;
  
  const resultsElement = container.querySelector('.quantum-test-results');
  const testButton = container.querySelector('.start-test-button');
  
  if (testButton) {
    testButton.addEventListener('click', function() {
      runQuantumTest(resultsElement);
    });
  }
  
  // 初始化清除测试结果按钮
  const clearButton = container.querySelector('.clear-test-button');
  if (clearButton && resultsElement) {
    clearButton.addEventListener('click', function() {
      resultsElement.innerHTML = '';
      resultsElement.appendChild(document.createTextNode('测试结果已清除'));
    });
  }
}

/**
 * 运行量子测试
 */
function runQuantumTest(resultsElement) {
  if (!resultsElement) return;
  
  // 清空之前的结果
  resultsElement.innerHTML = '';
  
  // 添加测试开始消息
  addTestResult(resultsElement, '开始量子叠加态测试...', 'info');
  
  // 模拟测试进度
  let progress = 0;
  const testInterval = setInterval(() => {
    progress += 10;
    
    if (progress <= 100) {
      addTestResult(resultsElement, `测试进度: ${progress}%`, 'progress');
      
      if (progress % 30 === 0) {
        // 随机生成一些测试数据
        const data = generateTestData();
        addTestResult(resultsElement, `量子状态: ${data.state}`, 'state');
        addTestResult(resultsElement, `纠缠程度: ${data.entanglement}`, 'info');
        addTestResult(resultsElement, `量子相干性: ${data.coherence}`, 'info');
      }
    } else {
      clearInterval(testInterval);
      addTestResult(resultsElement, '测试完成', 'success');
      
      // 显示测试总结
      const summary = generateTestSummary();
      addTestResult(resultsElement, '测试总结:', 'info');
      addTestResult(resultsElement, `- 量子态稳定性: ${summary.stability}`, 'info');
      addTestResult(resultsElement, `- 量子纠缠效率: ${summary.efficiency}`, 'info');
      addTestResult(resultsElement, `- 量子计算能力评分: ${summary.performance}`, 'success');
    }
  }, 300);
}

/**
 * 添加测试结果到输出元素
 */
function addTestResult(element, text, type = 'info') {
  const line = document.createElement('div');
  line.className = `console-line ${type}`;
  line.textContent = text;
  element.appendChild(line);
  
  // 自动滚动到底部
  element.scrollTop = element.scrollHeight;
}

/**
 * 生成测试数据
 */
function generateTestData() {
  const states = ['|0⟩', '|1⟩', '|+⟩', '|-⟩', '|Ψ+⟩', '|Φ-⟩'];
  const state = states[Math.floor(Math.random() * states.length)];
  const entanglement = (Math.random() * 0.3 + 0.7).toFixed(4);
  const coherence = (Math.random() * 0.4 + 0.6).toFixed(4);
  
  return { state, entanglement, coherence };
}

/**
 * 生成测试总结
 */
function generateTestSummary() {
  const stability = (Math.random() * 20 + 80).toFixed(2) + '%';
  const efficiency = (Math.random() * 20 + 75).toFixed(2) + '%';
  const performance = Math.floor(Math.random() * 300 + 700);
  
  return { stability, efficiency, performance };
}

/**
 * 初始化量子体验功能
 */
function initQuantumExperience() {
  const container = document.querySelector('.quantum-experience');
  if (!container) return;
  
  // 创建量子粒子效果
  createQuantumParticles(container);
  
  // 初始化交互式演示
  initExperienceDemo(container);
}

/**
 * 创建量子粒子效果
 */
function createQuantumParticles(container) {
  const particlesElement = document.createElement('div');
  particlesElement.className = 'quantum-particles';
  container.appendChild(particlesElement);
  
  // 创建粒子
  for (let i = 0; i < 50; i++) {
    const particle = document.createElement('div');
    particle.className = 'quantum-particle';
    particle.style.width = `${Math.random() * 4 + 1}px`;
    particle.style.height = particle.style.width;
    particle.style.background = `rgba(58, 134, 255, ${Math.random() * 0.5 + 0.2})`;
    particle.style.left = `${Math.random() * 100}%`;
    particle.style.top = `${Math.random() * 100}%`;
    particle.style.animationDuration = `${Math.random() * 10 + 10}s`;
    particle.style.animationDelay = `${Math.random() * 5}s`;
    
    particlesElement.appendChild(particle);
  }
}

/**
 * 初始化量子体验演示
 */
function initExperienceDemo(container) {
  // 在这里添加量子体验特定功能
  console.log('量子体验功能已初始化');
}

/**
 * 初始化API客户端
 */
function initApiClient() {
  const container = document.querySelector('.api-client-container');
  if (!container) return;
  
  // 获取端点列表
  const endpoints = container.querySelectorAll('.api-endpoint');
  
  // 获取请求表单和响应区域
  const requestForm = container.querySelector('.api-request-form');
  const responseArea = container.querySelector('.api-response');
  
  // 为每个端点添加点击事件
  endpoints.forEach(endpoint => {
    endpoint.addEventListener('click', function() {
      // 移除其他端点的活动状态
      endpoints.forEach(ep => ep.classList.remove('active'));
      
      // 设置当前端点为活动状态
      endpoint.classList.add('active');
      
      // 获取端点数据
      const method = endpoint.querySelector('.api-endpoint-method').textContent;
      const path = endpoint.querySelector('.api-endpoint-path').textContent;
      const description = endpoint.getAttribute('data-description') || '';
      
      // 更新请求表单
      updateRequestForm(requestForm, method, path, description);
    });
  });
  
  // 处理表单提交
  if (requestForm) {
    requestForm.addEventListener('submit', function(e) {
      e.preventDefault();
      
      const method = requestForm.querySelector('#request-method').value;
      const url = requestForm.querySelector('#request-url').value;
      const body = requestForm.querySelector('#request-body').value;
      
      // 发送API请求
      sendApiRequest(method, url, body, responseArea);
    });
  }
}

/**
 * 更新API请求表单
 */
function updateRequestForm(form, method, path, description) {
  if (!form) return;
  
  // 更新方法
  const methodInput = form.querySelector('#request-method');
  if (methodInput) methodInput.value = method;
  
  // 更新URL
  const urlInput = form.querySelector('#request-url');
  if (urlInput) urlInput.value = path;
  
  // 更新描述
  const descriptionElement = form.querySelector('.api-description');
  if (descriptionElement) descriptionElement.textContent = description;
  
  // 更新请求体样例
  const bodyInput = form.querySelector('#request-body');
  if (bodyInput) {
    if (method === 'GET' || method === 'DELETE') {
      bodyInput.value = '';
      bodyInput.disabled = true;
    } else {
      bodyInput.disabled = false;
      
      // 生成样例请求体
      const exampleBody = generateExampleRequestBody(path);
      bodyInput.value = JSON.stringify(exampleBody, null, 2);
    }
  }
}

/**
 * 生成示例请求体
 */
function generateExampleRequestBody(path) {
  // 根据路径生成不同的示例请求体
  if (path.includes('quantum-registry')) {
    return {
      deviceQuantumGene: 'QG-DEVICE-' + Math.random().toString(36).substring(2, 10),
      sessionQuantumGene: 'QG-SESSION-' + Math.random().toString(36).substring(2, 10),
      modelName: 'QSM'
    };
  } else if (path.includes('quantum-interaction')) {
    return {
      channelId: 'ch-' + Math.random().toString(36).substring(2, 10),
      interactionType: 'text',
      content: '这是一条测试消息'
    };
  } else {
    return {
      data: 'example',
      timestamp: new Date().toISOString()
    };
  }
}

/**
 * 发送API请求
 */
function sendApiRequest(method, url, body, responseElement) {
  if (!responseElement) return;
  
  // 显示加载中
  responseElement.textContent = 'Loading...';
  
  // 构建请求选项
  const options = {
    method: method,
    headers: {
      'Content-Type': 'application/json',
      'Accept': 'application/json'
    }
  };
  
  // 添加请求体（如果有）
  if (method !== 'GET' && method !== 'DELETE' && body) {
    try {
      options.body = body;
    } catch (e) {
      responseElement.textContent = '错误: 无效的JSON格式';
      return;
    }
  }
  
  // 发送请求
  fetch(url, options)
    .then(response => {
      if (!response.ok) {
        throw new Error(`HTTP错误! 状态: ${response.status}`);
      }
      return response.json();
    })
    .then(data => {
      // 显示响应
      responseElement.textContent = JSON.stringify(data, null, 2);
    })
    .catch(error => {
      responseElement.textContent = `错误: ${error.message}`;
    });
} 

/*
/*
量子基因编码: QE-QSM-7CF31E5FE156
纠缠状态: 活跃
纠缠对象: ['Ref/ref_core.py']
纠缠强度: 0.98
*/*/

// 开发团队：中华 ZhoHo ，Claude 
