"""LoRA Rank升级工具: r=16→32
保留已有rank-16权重, 新维度零初始化(B)/Kaiming初始化(A)
用于E31六重升级前的checkpoint转换
"""
import torch
import sys

def upgrade_lora_checkpoint(input_path, output_path, old_r=16, new_r=32):
    """升级LoRA checkpoint的rank"""
    ckpt = torch.load(input_path, map_location='cpu')
    state = ckpt['model_state_dict']
    
    upgraded = {}
    upgraded_count = 0
    
    for key, tensor in state.items():
        if 'lora_B' in key and tensor.shape[-1] == old_r:
            # B: [d, old_r] → [d, new_r]
            d = tensor.shape[0]
            new_tensor = torch.zeros(d, new_r)
            new_tensor[:, :old_r] = tensor  # 保留旧权重
            new_tensor[:, old_r:] = 0       # 新维度=0(lora标准)
            upgraded[key] = new_tensor
            upgraded_count += 1
            print(f"  升级 {key}: [{d},{old_r}]→[{d},{new_r}]")
        elif 'lora_A' in key and tensor.shape[0] == old_r:
            # A: [old_r, d] → [new_r, d]
            d = tensor.shape[-1]
            new_tensor = torch.zeros(new_r, d)
            new_tensor[:old_r, :] = tensor  # 保留旧权重
            # 新行用Kaiming初始化
            torch.nn.init.kaiming_uniform_(new_tensor[old_r:, :], a=5**0.5)
            upgraded[key] = new_tensor
            upgraded_count += 1
            print(f"  升级 {key}: [{old_r},{d}]→[{new_r},{d}]")
        else:
            upgraded[key] = tensor
    
    ckpt['model_state_dict'] = upgraded
    ckpt['lora_r'] = new_r
    torch.save(ckpt, output_path)
    print(f"\n✅ 升级完成! {upgraded_count}个LoRA矩阵 r={old_r}→{new_r}")
    print(f"保存: {output_path}")

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("用法: python upgrade_lora_r32.py <input.pth> <output.pth>")
        sys.exit(1)
    upgrade_lora_checkpoint(sys.argv[1], sys.argv[2])
