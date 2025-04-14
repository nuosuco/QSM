
# # 量子基因编码: QE-FIX-A4245B35A7AF
# # 纠缠状态: 活跃
# # 纠缠对象: []
# # 纠缠强度: 0.98
@echo off
chcp 65001 >nul

Set-Content -Path 'Ref/utils/quantum_gene_marker.py.new' -Encoding UTF8 -Value ([System.IO.File]::ReadAllText('Ref/utils/quantum_gene_marker.py.bak') -replace 'os.walk\(path\)', 'os.walk(path)', 0)
Rename-Item -Path 'Ref/utils/quantum_gene_marker.py.new' -NewName 'Ref/utils/quantum_gene_marker.py' -Force
