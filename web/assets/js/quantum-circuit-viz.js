/**
 * QSM - 量子电路可视化组件
 * 版本: v0.1.0
 * 量子基因编码: QGC-CIRCUIT-VIZ-20260302
 * 
 * 在Web界面可视化量子电路
 */

class QuantumCircuitVisualizer {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.gates = [];
        this.qubits = 4;
        this.circuitWidth = 800;
        this.gateSize = 40;
        this.wireSpacing = 50;
    }

    // 添加量子门到电路
    addGate(type, qubit, position, controlQubit = null) {
        this.gates.push({
            type: type,
            qubit: qubit,
            position: position,
            controlQubit: controlQubit,
            id: `gate-${Date.now()}-${Math.random().toString(36).substr(2,9)}`
        });
        this.render();
    }

    // 清空电路
    clear() {
        this.gates = [];
        this.render();
    }

    // 渲染电路
    render() {
        if (!this.container) return;

        let html = `<div class="quantum-circuit" style="position: relative; width: ${this.circuitWidth}px; padding: 20px; background: rgba(0,0,0,0.3); border-radius: 10px;">`;
        
        // 绘制量子线
        for (let i = 0; i < this.qubits; i++) {
            const y = 30 + i * this.wireSpacing;
            html += `
                <div style="position: absolute; left: 60px; top: ${y}px; width: ${this.circuitWidth - 80}px; height: 2px; background: rgba(138, 135, 255, 0.5);"></div>
                <div style="position: absolute; left: 10px; top: ${y - 10}px; color: #8a87ff; font-family: monospace; font-size: 14px;">q${i}</div>
                <div style="position: absolute; right: 20px; top: ${y - 10}px; color: rgba(255,255,255,0.5); font-family: monospace; font-size: 12px;">|0⟩</div>
            `;
        }

        // 绘制量子门
        this.gates.forEach(gate => {
            const x = 80 + gate.position * 60;
            const y = 30 + gate.qubit * this.wireSpacing;
            html += this.renderGate(gate, x, y);
        });

        html += '</div>';
        this.container.innerHTML = html;
    }

    // 渲染单个门
    renderGate(gate, x, y) {
        const colors = {
            'H': '#4ecdc4',
            'X': '#ff6b6b',
            'Y': '#ffe66d',
            'Z': '#95e1d3',
            'S': '#dfe6e9',
            'T': '#ffeaa7',
            'CNOT': '#ff6b6b',
            'SWAP': '#74b9ff',
            'MEASURE': '#a29bfe'
        };

        const color = colors[gate.type] || '#8a87ff';
        let html = '';

        if (gate.type === 'CNOT' && gate.controlQubit !== null) {
            // 绘制CNOT门（带控制线）
            const controlY = 30 + gate.controlQubit * this.wireSpacing;
            html += `<div style="position: absolute; left: ${x}px; top: ${controlY}px; width: 2px; height: ${Math.abs(y - controlY)}px; background: ${color};"></div>`;
            html += `<div style="position: absolute; left: ${x - 4}px; top: ${controlY - 4}px; width: 10px; height: 10px; background: ${color}; border-radius: 50%;"></div>`;
        }

        // 绘制门框
        html += `
            <div class="quantum-gate" data-gate-id="${gate.id}" style="
                position: absolute;
                left: ${x - this.gateSize/2}px;
                top: ${y - this.gateSize/2}px;
                width: ${this.gateSize}px;
                height: ${this.gateSize}px;
                background: ${color};
                border-radius: 8px;
                display: flex;
                align-items: center;
                justify-content: center;
                font-family: monospace;
                font-weight: bold;
                font-size: 16px;
                color: #1a1a2e;
                cursor: pointer;
                box-shadow: 0 2px 10px rgba(0,0,0,0.3);
                transition: transform 0.2s, box-shadow 0.2s;
            " onmouseover="this.style.transform='scale(1.1)'" onmouseout="this.style.transform='scale(1)'">
                ${gate.type}
            </div>
        `;

        return html;
    }

    // 从QBC代码解析电路
    parseQBC(qbcCode) {
        this.clear();
        const lines = qbcCode.split('\n');
        let position = 0;

        lines.forEach(line => {
            line = line.trim();
            if (!line || line.startsWith('#')) return;

            const parts = line.split(/\s+/);
            const opcode = parts[0].toUpperCase();

            switch(opcode) {
                case 'H':
                case 'X':
                case 'Y':
                case 'Z':
                case 'S':
                case 'T':
                    this.addGate(opcode, parseInt(parts[1].replace('q', '')), position);
                    position++;
                    break;
                case 'CNOT':
                    const control = parseInt(parts[1].replace('q', ''));
                    const target = parseInt(parts[2].replace('q', ''));
                    this.addGate('CNOT', target, position, control);
                    position++;
                    break;
                case 'MEASURE':
                    this.addGate('MEASURE', parseInt(parts[1].replace('q', '')), position);
                    position++;
                    break;
            }
        });
    }

    // 导出为图片（使用canvas）
    exportAsImage() {
        // 简化版本：返回SVG字符串
        let svg = `<svg width="${this.circuitWidth}" height="${this.qubits * this.wireSpacing + 60}" xmlns="http://www.w3.org/2000/svg">`;
        
        // 背景
        svg += `<rect width="100%" height="100%" fill="#1a1a2e"/>`;
        
        // 量子线
        for (let i = 0; i < this.qubits; i++) {
            const y = 30 + i * this.wireSpacing;
            svg += `<line x1="60" y1="${y}" x2="${this.circuitWidth - 20}" y2="${y}" stroke="rgba(138, 135, 255, 0.5)" stroke-width="2"/>`;
            svg += `<text x="10" y="${y + 5}" fill="#8a87ff" font-family="monospace" font-size="14">q${i}</text>`;
        }

        // 量子门
        this.gates.forEach(gate => {
            const x = 80 + gate.position * 60;
            const y = 30 + gate.qubit * this.wireSpacing;
            const colors = {
                'H': '#4ecdc4', 'X': '#ff6b6b', 'Y': '#ffe66d',
                'Z': '#95e1d3', 'S': '#dfe6e9', 'T': '#ffeaa7'
            };
            const color = colors[gate.type] || '#8a87ff';
            svg += `<rect x="${x - 20}" y="${y - 20}" width="40" height="40" rx="8" fill="${color}"/>`;
            svg += `<text x="${x}" y="${y + 6}" text-anchor="middle" fill="#1a1a2e" font-family="monospace" font-weight="bold" font-size="16">${gate.type}</text>`;
        });

        svg += '</svg>';
        return svg;
    }
}

// 导出到全局
window.QuantumCircuitVisualizer = QuantumCircuitVisualizer;

// ========== 拖拽交互系统 ==========

// 初始化拖拽功能
initDragDrop() {
  if (!this.container) return;
  
  // 创建门工具栏
  this.createGateToolbar();
  
  // 设置拖放目标
  this.container.addEventListener('dragover', (e) => {
    e.preventDefault();
    e.dataTransfer.dropEffect = 'copy';
  });
  
  this.container.addEventListener('drop', (e) => {
    e.preventDefault();
    const gateType = e.dataTransfer.getData('gateType');
    if (gateType) {
      const rect = this.container.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;
      
      // 计算量子比特和位置
      const qubit = Math.floor(y / this.wireSpacing);
      const position = Math.floor(x / this.gateSize);
      
      if (qubit >= 0 && qubit < this.qubits && position >= 0) {
        this.addGate(gateType, qubit, position);
        if (window.logMessage) {
          window.logMessage(`✅ 添加 ${gateType} 门到 q${qubit}, 位置${position}`);
        }
      }
    }
  });
}

// 创建门工具栏
createGateToolbar() {
  if (this.toolbar) return;
  
  this.toolbar = document.createElement('div');
  this.toolbar.className = 'gate-toolbar';
  this.toolbar.style.cssText = `
    display: flex;
    gap: 8px;
    padding: 10px;
    background: rgba(138, 135, 255, 0.1);
    border-radius: 8px;
    margin-bottom: 10px;
    flex-wrap: wrap;
  `;
  
  const gates = [
    { type: 'H', label: 'H', color: '#8a87ff', title: 'Hadamard门' },
    { type: 'X', label: 'X', color: '#ff6b6b', title: 'NOT门' },
    { type: 'Y', label: 'Y', color: '#4ecdc4', title: 'Pauli Y门' },
    { type: 'Z', label: 'Z', color: '#ffe66d', title: 'Pauli Z门' },
    { type: 'S', label: 'S', color: '#95e1d3', title: '相位门' },
    { type: 'T', label: 'T', color: '#f38181', title: 'T门' },
    { type: 'MEASURE', label: 'M', color: '#aaa', title: '测量' }
  ];
  
  gates.forEach(gate => {
    const btn = document.createElement('div');
    btn.className = 'gate-tool';
    btn.draggable = true;
    btn.textContent = gate.label;
    btn.title = gate.title;
    btn.style.cssText = `
      width: 36px;
      height: 36px;
      background: ${gate.color};
      border-radius: 6px;
      display: flex;
      align-items: center;
      justify-content: center;
      font-weight: bold;
      cursor: grab;
      color: #fff;
      text-shadow: 0 1px 2px rgba(0,0,0,0.3);
    `;
    
    btn.addEventListener('dragstart', (e) => {
      e.dataTransfer.setData('gateType', gate.type);
    });
    
    this.toolbar.appendChild(btn);
  });
  
  // 插入到容器前面
  this.container.parentNode.insertBefore(this.toolbar, this.container);
}

// 清空电路
clearCircuit() {
  this.gates = [];
  this.render();
  if (window.logMessage) {
    window.logMessage('🗑️ 电路已清空');
  }
}

// 导出电路为QBC代码
exportToQBC() {
  if (this.gates.length === 0) {
    return '# 空电路\n# 从工具栏拖拽量子门到电路中';
  }
  
  let qbc = '# 量子电路\n';
  qbc += '# 自动生成: ' + new Date().toISOString() + '\n\n';
  
  // 按位置排序
  const sortedGates = [...this.gates].sort((a, b) => a.position - b.position);
  
  sortedGates.forEach(gate => {
    if (gate.type === 'MEASURE') {
      qbc += `MEASURE q${gate.qubit}\n`;
    } else if (gate.controlQubit !== null) {
      qbc += `CNOT q${gate.controlQubit} q${gate.qubit}\n`;
    } else {
      qbc += `${gate.type} q${gate.qubit}\n`;
    }
  });
  
  return qbc;
}

// 从QBC代码导入
importFromQBC(qbcCode) {
  this.gates = [];
  const lines = qbcCode.split('\n');
  let position = 0;
  
  lines.forEach(line => {
    line = line.trim();
    if (!line || line.startsWith('#')) return;
    
    const parts = line.split(/\s+/);
    const gateType = parts[0];
    
    if (gateType === 'MEASURE') {
      const qubit = parseInt(parts[1].replace('q', ''));
      this.addGate('MEASURE', qubit, position++);
    } else if (['H', 'X', 'Y', 'Z', 'S', 'T'].includes(gateType)) {
      const qubit = parseInt(parts[1].replace('q', ''));
      this.addGate(gateType, qubit, position++);
    } else if (gateType === 'CNOT') {
      const control = parseInt(parts[1].replace('q', ''));
      const target = parseInt(parts[2].replace('q', ''));
      this.addGate('CNOT', target, position++, control);
    }
  });
  
  this.render();
}


// ========== 文件保存/加载系统 ==========

// 保存电路到localStorage
saveCircuit(name = 'default') {
  const data = {
    name: name,
    qubits: this.qubits,
    gates: this.gates,
    createdAt: new Date().toISOString()
  };
  
  try {
    localStorage.setItem(`qvm-circuit-${name}`, JSON.stringify(data));
    if (window.logMessage) {
      window.logMessage(`💾 电路已保存: ${name}`);
    }
    return { success: true, message: `电路已保存为 "${name}"` };
  } catch (e) {
    return { success: false, error: '保存失败: ' + e.message };
  }
}

// 从localStorage加载电路
loadCircuit(name = 'default') {
  try {
    const data = localStorage.getItem(`qvm-circuit-${name}`);
    if (!data) {
      return { success: false, error: '未找到保存的电路' };
    }
    
    const parsed = JSON.parse(data);
    this.qubits = parsed.qubits || 4;
    this.gates = parsed.gates || [];
    this.render();
    
    if (window.logMessage) {
      window.logMessage(`📂 已加载电路: ${name}`);
    }
    return { success: true, message: `已加载电路 "${name}"` };
  } catch (e) {
    return { success: false, error: '加载失败: ' + e.message };
  }
}

// 获取所有已保存的电路列表
listSavedCircuits() {
  const circuits = [];
  for (let i = 0; i < localStorage.length; i++) {
    const key = localStorage.key(i);
    if (key && key.startsWith('qvm-circuit-')) {
      try {
        const data = JSON.parse(localStorage.getItem(key));
        circuits.push({
          name: key.replace('qvm-circuit-', ''),
          qubits: data.qubits,
          gateCount: data.gates ? data.gates.length : 0,
          createdAt: data.createdAt
        });
      } catch (e) {}
    }
  }
  return circuits;
}

// 删除已保存的电路
deleteCircuit(name) {
  localStorage.removeItem(`qvm-circuit-${name}`);
  if (window.logMessage) {
    window.logMessage(`🗑️ 已删除电路: ${name}`);
  }
}

// 导出电路为JSON文件
exportToFile(filename = 'circuit.json') {
  const data = {
    version: '0.2.0',
    qubits: this.qubits,
    gates: this.gates,
    exportedAt: new Date().toISOString()
  };
  
  const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
  
  if (window.logMessage) {
    window.logMessage(`📤 电路已导出: ${filename}`);
  }
}

// 从JSON文件导入电路
importFromFile(file) {
  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    reader.onload = (e) => {
      try {
        const data = JSON.parse(e.target.result);
        this.qubits = data.qubits || 4;
        this.gates = data.gates || [];
        this.render();
        if (window.logMessage) {
          window.logMessage(`📥 已导入电路 (${this.gates.length} 个门)`);
        }
        resolve({ success: true, message: '导入成功' });
      } catch (err) {
        reject({ success: false, error: '文件格式错误' });
      }
    };
    reader.onerror = () => reject({ success: false, error: '读取文件失败' });
    reader.readAsText(file);
  });
}


// ========== 预设电路库 ==========

// 预设电路定义
static getPresetCircuits() {
  return [
    {
      name: 'Bell态制备',
      description: '创建两量子比特的最大纠缠态',
      qubits: 2,
      gates: [
        { type: 'H', qubit: 0, position: 0 },
        { type: 'CNOT', qubit: 1, position: 1, controlQubit: 0 }
      ]
    },
    {
      name: 'GHZ态制备',
      description: '创建三量子比特GHZ纠缠态',
      qubits: 3,
      gates: [
        { type: 'H', qubit: 0, position: 0 },
        { type: 'CNOT', qubit: 1, position: 1, controlQubit: 0 },
        { type: 'CNOT', qubit: 2, position: 2, controlQubit: 0 }
      ]
    },
    {
      name: '量子隐形传态',
      description: '完整量子隐形传态电路',
      qubits: 3,
      gates: [
        { type: 'H', qubit: 1, position: 0 },
        { type: 'CNOT', qubit: 2, position: 1, controlQubit: 1 },
        { type: 'CNOT', qubit: 0, position: 2, controlQubit: 1 },
        { type: 'H', qubit: 0, position: 3 },
        { type: 'MEASURE', qubit: 0, position: 4 },
        { type: 'MEASURE', qubit: 1, position: 4 }
      ]
    },
    {
      name: 'Deutsch算法',
      description: '判断函数是常数还是平衡',
      qubits: 2,
      gates: [
        { type: 'X', qubit: 1, position: 0 },
        { type: 'H', qubit: 0, position: 1 },
        { type: 'H', qubit: 1, position: 1 },
        { type: 'CNOT', qubit: 1, position: 2, controlQubit: 0 },
        { type: 'H', qubit: 0, position: 3 },
        { type: 'MEASURE', qubit: 0, position: 4 }
      ]
    },
    {
      name: 'QFT 2比特',
      description: '2量子比特傅里叶变换',
      qubits: 2,
      gates: [
        { type: 'H', qubit: 0, position: 0 },
        { type: 'CNOT', qubit: 1, position: 1, controlQubit: 0 },
        { type: 'H', qubit: 1, position: 2 },
        { type: 'SWAP', qubit: 0, position: 3, controlQubit: 1 }
      ]
    },
    {
      name: 'Grover迭代',
      description: 'Grover搜索单次迭代',
      qubits: 2,
      gates: [
        { type: 'H', qubit: 0, position: 0 },
        { type: 'H', qubit: 1, position: 0 },
        { type: 'X', qubit: 0, position: 1 },
        { type: 'X', qubit: 1, position: 1 },
        { type: 'H', qubit: 1, position: 2 },
        { type: 'CNOT', qubit: 1, position: 3, controlQubit: 0 },
        { type: 'H', qubit: 1, position: 4 },
        { type: 'X', qubit: 0, position: 5 },
        { type: 'X', qubit: 1, position: 5 },
        { type: 'H', qubit: 0, position: 6 },
        { type: 'H', qubit: 1, position: 6 }
      ]
    }
  ];
}

// 加载预设电路
loadPreset(name) {
  const presets = QuantumCircuitVisualizer.getPresetCircuits();
  const preset = presets.find(p => p.name === name);
  
  if (!preset) {
    return { success: false, error: '未找到预设电路' };
  }
  
  this.qubits = preset.qubits;
  this.gates = preset.gates.map((g, i) => ({
    ...g,
    id: `preset-${Date.now()}-${i}`
  }));
  this.render();
  
  if (window.logMessage) {
    window.logMessage(`📋 已加载预设: ${name}`);
  }
  return { success: true, message: `已加载 "${name}"` };
}

