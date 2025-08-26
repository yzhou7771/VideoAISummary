#!/usr/bin/env python3
"""
创建一个简单的扩展图标
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_simple_icon():
    # 创建 128x128 的图像
    size = (128, 128)
    
    # 创建红色背景 (YouTube 红色)
    img = Image.new('RGB', size, color='#FF0000')
    draw = ImageDraw.Draw(img)
    
    # 添加白色圆形背景
    margin = 16
    circle_bbox = [margin, margin, size[0]-margin, size[1]-margin]
    draw.ellipse(circle_bbox, fill='white')
    
    # 添加播放按钮三角形
    triangle_size = 32
    center_x, center_y = size[0] // 2, size[1] // 2
    
    # 三角形坐标 (播放按钮)
    triangle = [
        (center_x - triangle_size//2, center_y - triangle_size//2),
        (center_x - triangle_size//2, center_y + triangle_size//2),
        (center_x + triangle_size//2, center_y)
    ]
    
    draw.polygon(triangle, fill='#FF0000')
    
    # 添加文字 "YT"
    try:
        # 尝试使用系统字体
        font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 20)
    except:
        # 如果没有找到字体，使用默认字体
        font = ImageFont.load_default()
    
    text = "YT"
    # 获取文字尺寸
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    
    # 在底部居中显示文字
    text_x = (size[0] - text_width) // 2
    text_y = size[1] - 30
    
    draw.text((text_x, text_y), text, fill='white', font=font)
    
    # 保存图标
    icon_path = 'extension/icons/icon128.png'
    os.makedirs(os.path.dirname(icon_path), exist_ok=True)
    img.save(icon_path)
    print(f"✅ 图标已创建: {icon_path}")
    
    return icon_path

def main():
    try:
        create_simple_icon()
        print("🎉 扩展图标创建成功！")
    except ImportError:
        print("❌ 需要安装 Pillow 库来创建图标")
        print("💡 运行: pip install Pillow")
        print("或者手动放置一个128x128的PNG图标到 extension/icons/icon128.png")
    except Exception as e:
        print(f"❌ 创建图标时出错: {e}")
        print("💡 请手动放置一个128x128的PNG图标到 extension/icons/icon128.png")

if __name__ == "__main__":
    main()