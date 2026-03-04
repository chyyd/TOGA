# -*- coding: utf-8 -*-
"""PDF生成模块"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from datetime import datetime, timedelta
import os

class PDFGenerator:
    """生成治疗记录单PDF"""
    
    def __init__(self):
        # 注册中文字体
        self._register_font()
        self.page_width, self.page_height = A4
    
    def _register_font(self):
        """注册中文字体"""
        # 尝试使用系统字体
        font_paths = [
            'C:/Windows/Fonts/simhei.ttf',  # Windows 黑体
            'C:/Windows/Fonts/msyh.ttc',     # Windows 微软雅黑
            'C:/Windows/Fonts/simsun.ttc',   # Windows 宋体
            '/System/Library/Fonts/PingFang.ttc',  # macOS
            '/usr/share/fonts/truetype/wqy/wqy-zenhei.ttc',  # Linux
        ]
        
        self.font_name = 'ChineseFont'
        for path in font_paths:
            if os.path.exists(path):
                try:
                    pdfmetrics.registerFont(TTFont(self.font_name, path))
                    return
                except:
                    continue
        
        # 如果找不到字体，使用默认字体（可能无法正确显示中文）
        self.font_name = 'Helvetica'
    
    def generate(self, patient_name, hospital_no, diagnosis_name, treatment_name,
                 treatment_details, start_date, output_path, hospital_name='', surcharge_info=''):
        """生成PDF"""
        c = canvas.Canvas(output_path, pagesize=A4)
        
        # 绘制标题，返回下一个可用的y坐标
        y_after_header = self._draw_header(c, hospital_name, patient_name, hospital_no, 
                          diagnosis_name, treatment_name, start_date)
        
        # 绘制治疗内容，紧密衔接
        y_after_content = self._draw_treatment_details(c, treatment_details, y_after_header)
        
        # 绘制加收信息（如果有）
        y_after_surcharge = self._draw_surcharge(c, surcharge_info, y_after_content)
        
        # 绘制90天表格
        self._draw_table(c, start_date, y_after_surcharge - 3*mm)
        
        c.save()
        return output_path
    
    def _draw_header(self, c, hospital_name, patient_name, hospital_no,
                     diagnosis_name, treatment_name, start_date):
        """绘制表头信息，返回下一个可用的y坐标"""
        y = self.page_height - 10 * mm  # 从顶部10mm开始
        
        # 医院名称（如果有）
        if hospital_name:
            c.setFont(self.font_name, 14)
            c.drawCentredString(self.page_width / 2, y, hospital_name)
            y -= 7 * mm
        
        # 标题
        c.setFont(self.font_name, 16)
        c.drawCentredString(self.page_width / 2, y, "治疗记录单")
        y -= 8 * mm
        
        # 患者信息行
        c.setFont(self.font_name, 10)
        info_text = f"姓名：{patient_name}"
        if hospital_no:
            info_text += f"    住院号：{hospital_no}"
        info_text += f"    诊断：{diagnosis_name}"
        c.drawString(15 * mm, y, info_text)
        y -= 6 * mm
        
        # 治疗项目行
        start_date_str = start_date.strftime('%Y-%m-%d')
        c.drawString(15 * mm, y, f"治疗项目：{treatment_name}    开始日期：{start_date_str}")
        y -= 6 * mm
        
        return y
    
    def _draw_treatment_details(self, c, treatment_details, y_start):
        """绘制治疗内容，返回下一个可用的y坐标"""
        y = y_start
        
        c.setFont(self.font_name, 10)
        
        # 处理长文本换行
        max_width = self.page_width - 35 * mm
        words = "治疗内容：" + treatment_details
        lines = []
        current_line = ""
        
        for char in words:
            test_line = current_line + char
            if c.stringWidth(test_line, self.font_name, 10) < max_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = char
        if current_line:
            lines.append(current_line)
        
        # 绘制治疗内容，最多2行
        for i, line in enumerate(lines[:2]):
            c.drawString(15 * mm, y, line)
            y -= 4.5 * mm
        
        return y
    
    def _draw_surcharge(self, c, surcharge_info, y_start):
        """绘制加收信息，返回下一个可用的y坐标"""
        if not surcharge_info:
            return y_start
        
        y = y_start
        c.setFont(self.font_name, 10)
        c.drawString(15 * mm, y, f"加收：{surcharge_info}")
        y -= 4.5 * mm
        
        return y
    
    def _draw_table(self, c, start_date, y_start):
        """绘制90天表格（3列×30行）"""
        margin_left = 10 * mm
        margin_right = 10 * mm
        
        # 表格尺寸 - 三列之间无间隔
        total_width = self.page_width - margin_left - margin_right
        col_width = total_width / 3
        actual_col_width = col_width  # 无间隙
        
        # 行高计算
        available_height = y_start - 10 * mm  # 底部留10mm边距
        row_height = available_height / 31  # 30行数据 + 1行表头
        
        # 表格顶部y坐标
        table_top = y_start
        
        # 表格列定义 - 日期列缩小，其他列增大方便手写
        headers = ['日  期', '时  间', '操作者', '患者签字']
        col_widths = [actual_col_width * 0.18, actual_col_width * 0.28, 
                      actual_col_width * 0.27, actual_col_width * 0.27]
        
        # 绘制3列表格
        for col in range(3):
            x = margin_left + col * col_width
            
            # 绘制表头（占一行）
            self._draw_table_header(c, x, table_top, col_widths, headers, row_height)
            
            # 绘制30行数据（从第2行开始）
            start_day = col * 30
            for row in range(30):
                # 第i行数据的y坐标：表头顶部 - (i+2) * row_height
                y = table_top - (row + 2) * row_height
                day_offset = start_day + row
                current_date = start_date + timedelta(days=day_offset)
                
                # 简化日期格式：3/2一
                weekdays = ['一', '二', '三', '四', '五', '六', '日']
                weekday = weekdays[current_date.weekday()]
                date_str = f"{current_date.month}/{current_date.day} {weekday}"
                
                self._draw_table_row(c, x, y, col_widths, [date_str, '', '', ''], row_height)
            
            # 绘制该列完整边框
            self._draw_col_outline(c, x, table_top, col_widths, row_height * 31)
        
        # 绘制整体外框线
        self._draw_table_outline(c, margin_left, table_top, total_width, 31 * row_height)
    
    def _draw_table_header(self, c, x, y, col_widths, headers, row_height):
        """绘制表头行"""
        c.setFont(self.font_name, 8)
        
        # 绘制背景色（浅灰色）和边框
        c.setFillColorRGB(0.9, 0.9, 0.9)
        c.setStrokeColorRGB(0, 0, 0)
        c.setLineWidth(1)
        c.rect(x, y - row_height, sum(col_widths), row_height, fill=True, stroke=True)
        c.setFillColorRGB(0, 0, 0)
        
        # 绘制文字 - 居中
        current_x = x
        for i, (header, width) in enumerate(zip(headers, col_widths)):
            text_y = y - row_height / 2 - 2  # 文字垂直居中
            c.drawCentredString(current_x + width / 2, text_y, header)
            current_x += width
            # 绘制列分隔线
            if i < len(headers) - 1:
                c.line(current_x, y - row_height, current_x, y)
        
        # 绘制上边框（加粗）
        c.setLineWidth(1.5)
        c.line(x, y, x + sum(col_widths), y)
    
    def _draw_table_row(self, c, x, y, col_widths, values, row_height):
        """绘制数据行"""
        c.setFont(self.font_name, 7)
        c.setLineWidth(0.5)
        c.setStrokeColorRGB(0, 0, 0)
        
        total_width = sum(col_widths)
        
        # 绘制行的左右边界和底边
        c.line(x, y, x, y + row_height)  # 左边
        c.line(x + total_width, y, x + total_width, y + row_height)  # 右边
        c.line(x, y, x + total_width, y)  # 底边
        
        # 绘制列分隔线
        current_x = x
        for i, (value, width) in enumerate(zip(values, col_widths)):
            if i < len(col_widths) - 1:
                current_x += width
                c.line(current_x, y, current_x, y + row_height)
            
            # 绘制文字 - 垂直居中
            if value:
                text_y = y + row_height / 2 - 2
                c.drawCentredString(x + sum(col_widths[:i]) + width / 2, text_y, value)
    
    def _draw_col_outline(self, c, x, y, col_widths, height):
        """绘制单列外框线"""
        total_width = sum(col_widths)
        
        # 列分隔线（细线）
        c.setLineWidth(0.5)
        c.setStrokeColorRGB(0, 0, 0)
        current_x = x
        for i, width in enumerate(col_widths[:-1]):
            current_x += width
            c.line(current_x, y, current_x, y - height)
    
    def _draw_table_outline(self, c, x, y, width, height):
        """绘制表格整体外框线"""
        c.setLineWidth(2)
        c.setStrokeColorRGB(0, 0, 0)
        c.rect(x, y - height, width, height, fill=False, stroke=True)
