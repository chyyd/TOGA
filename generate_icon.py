import os
from PIL import Image, ImageDraw, ImageFont

def create_medical_icon():
    # 创建不同尺寸的图标
    sizes = [256, 128, 64, 48, 32, 16]
    icon_images = []
    
    for size in sizes:
        # 创建图像
        img = Image.new('RGBA', (size, size), (255, 255, 255, 0))
        draw = ImageDraw.Draw(img)
        
        # 绘制文档形状
        margin = size // 8
        doc_width = size - 2 * margin
        doc_height = int(size * 0.8)
        doc_x = margin
        doc_y = (size - doc_height) // 2
        
        # 文档主体
        draw.rounded_rectangle(
            [(doc_x, doc_y), (doc_x + doc_width, doc_y + doc_height)], 
            radius=size//8, 
            fill=(255, 255, 255, 255), 
            outline=(50, 50, 150, 255), 
            width=max(1, size//32)
        )
        
        # 文档上的线条
        line_margin = size // 6
        line_height = size // 12
        for i in range(3):
            y_pos = doc_y + line_margin + i * line_height * 1.5
            draw.line(
                [(doc_x + line_margin, y_pos), (doc_x + doc_width - line_margin, y_pos)], 
                fill=(0, 0, 0, 200), 
                width=max(1, size//32)
            )
        
        # 添加十字标志（医疗符号）
        cross_size = size // 4
        cross_x = size - margin - cross_size
        cross_y = doc_y + margin
        
        # 水平线
        draw.rectangle(
            [(cross_x, cross_y + cross_size//2 - max(1, size//32)//2), 
             (cross_x + cross_size, cross_y + cross_size//2 + max(1, size//32)//2)], 
            fill=(220, 50, 50, 255)
        )
        # 垂直线
        draw.rectangle(
            [(cross_x + cross_size//2 - max(1, size//32)//2, cross_y), 
             (cross_x + cross_size//2 + max(1, size//32)//2, cross_y + cross_size)], 
            fill=(220, 50, 50, 255)
        )
        
        icon_images.append(img)
    
    # 保存为ICO文件
    icon_images[0].save(
        '治疗记录单生成器图标.ico',
        format='ICO',
        append_images=icon_images[1:],
        sizes=[(s, s) for s in sizes]
    )
    
    print("图标已生成: 治疗记录单生成器图标.ico")

if __name__ == "__main__":
    try:
        create_medical_icon()
    except ImportError:
        print("需要安装Pillow库来生成图标。")
        print("请运行: pip install Pillow")