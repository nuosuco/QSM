"""
环境变量加载器 - 解决.env文件加载问题
"""
import os
from pathlib import Path


def load_env_file(env_path: str = None) -> dict:
    """
    加载环境变量文件到Python环境
    
    Args:
        env_path: .env文件路径，默认 ~/.qnt_env
    
    Returns:
        加载的环境变量字典
    """
    if env_path is None:
        env_path = str(Path.home() / '.qnt_env')
    
    env_file = Path(env_path)
    
    if not env_file.exists():
        raise FileNotFoundError(f"环境变量文件不存在: {env_path}")
    
    loaded = {}
    for line in open(env_file):
        line = line.strip()
        # 跳过空行和注释
        if not line or line.startswith('#'):
            continue
        # 解析 KEY=VALUE 格式
        if '=' in line:
            key, _, value = line.partition('=')
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            os.environ[key] = value
            loaded[key] = value
    
    return loaded


def get_bitget_keys() -> tuple:
    """
    获取Bitget API密钥
    
    Returns:
        (api_key, api_secret, api_passphrase)
    """
    # 确保环境变量已加载
    load_env_file()
    
    api_key = os.getenv('BITGET_API_KEY')
    api_secret = os.getenv('BITGET_API_SECRET')
    api_passphrase = os.getenv('BITGET_API_PASSPHRASE', 'qntsomtop')
    
    if not api_key or not api_secret:
        raise ValueError("API密钥未配置，请检查 ~/.qnt_env 文件")
    
    return api_key, api_secret, api_passphrase


if __name__ == '__main__':
    # 测试加载
    keys = get_bitget_keys()
    print(f"API Key: {keys[0][:10]}...")
    print(f"API Secret: {keys[1][:10]}...")
    print(f"Passphrase: {keys[2]}")