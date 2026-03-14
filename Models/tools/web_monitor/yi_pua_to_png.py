from PIL import Image, ImageDraw, ImageFont
import os

# 字体文件路径（相对web_monitor目录）
FONT_PATH = "fonts/msyi.ttf"
# 输出图片目录
OUTPUT_DIR = "yi_pua_png"
# 需要渲染的彝文PUA字符及含义
YI_PUA_CHARS = [
    ("󲜐", "陷害", "F1D10"),
    ("󲜑", "兔子", "F1D11"),
    ("󲜒", "卷",   "F1D12"),
    ("󲜓", "舔",   "F1D13"),
    ("󲜔", "便宜", "F1D14"),
    ("󲜕", "埋怨", "F1D15"),
    ("󲜖", "裱褙", "F1D16"),
    ("󲜗", "渣",   "F1D17"),
    ("󲜘", "尾",   "F1D18"),
    ("󲜙", "分开", "F1D19"),
    ("󲜚", "雪",   "F1D1A"),
    ("󲜛", "绊",   "F1D1B"),
    ("󲜜", "指",   "F1D1C"),
    ("󲜝", "包",   "F1D1D"),
    ("󲜞", "锐利", "F1D1E"),
]

os.makedirs(OUTPUT_DIR, exist_ok=True)
font = ImageFont.truetype(FONT_PATH, 64)

for char, meaning, code in YI_PUA_CHARS:
    img = Image.new("RGBA", (96, 96), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    bbox = draw.textbbox((0, 0), char, font=font)
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]
    draw.text(((96-w)//2, (96-h)//2), char, font=font, fill=(0,0,0,255))
    img.save(os.path.join(OUTPUT_DIR, f"yi_{code}.png"))
    print(f"生成: yi_{code}.png ({meaning})")

print("全部生成完毕！") 