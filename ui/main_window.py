# -*- coding: utf-8 -*-
"""主界面模块"""

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QDateEdit, QComboBox, QTextEdit, QPushButton,
    QMessageBox, QFileDialog, QCheckBox, QGroupBox, QFrame, QSizePolicy
)
from PyQt5.QtCore import Qt, QDate
from PyQt5.QtGui import QFont
import sys
import os

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.config_manager import ConfigManager
from core.pdf_generator import PDFGenerator
from ui.settings_dialog import SettingsDialog


class MainWindow(QMainWindow):
    """主窗口"""
    
    def __init__(self):
        super().__init__()
        self.config_manager = ConfigManager()
        self.pdf_generator = PDFGenerator()
        self.current_treatment_id = None
        self.init_ui()
    
    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle('治疗记录单生成器')
        # 最小窗口大小，允许纵向拉伸
        self.setMinimumSize(480, 520)
        
        # 创建中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(0)
        main_layout.setContentsMargins(20, 15, 20, 15)
        
        # 标题（固定大小）
        title_label = QLabel('治疗记录单生成器')
        title_label.setFont(QFont('Microsoft YaHei', 14, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFixedHeight(30)
        title_label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        main_layout.addWidget(title_label)
        
        # 分隔线
        main_layout.addWidget(self._create_separator())
        
        # 患者信息区（固定大小）
        info_group = QGroupBox('患者信息')
        info_group.setLayout(self._create_info_layout())
        info_group.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        main_layout.addWidget(info_group)
        
        # 治疗选择区（可纵向拉伸）
        treatment_group = QGroupBox('治疗信息')
        treatment_group.setLayout(self._create_treatment_content_layout())
        treatment_group.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        main_layout.addWidget(treatment_group, 1)  # 拉伸因子为1
        
        # 加收选项区（固定大小）
        self.surcharge_group = self._create_surcharge_group()
        self.surcharge_group.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        main_layout.addWidget(self.surcharge_group)
        
        # 分隔线
        main_layout.addWidget(self._create_separator())
        
        # 按钮区（固定大小）
        button_layout = self._create_button_layout()
        main_layout.addLayout(button_layout)
        
        # 加载初始数据
        self._load_treatments()
    
    def _create_separator(self):
        """创建分隔线"""
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        line.setFixedHeight(1)
        return line
    
    def _create_info_layout(self):
        """创建患者信息区域"""
        layout = QFormLayout()
        layout.setSpacing(6)
        layout.setContentsMargins(10, 5, 10, 5)
        layout.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        
        # 姓名
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText('请输入患者姓名')
        self.name_edit.setMaxLength(20)
        layout.addRow('姓名：', self.name_edit)
        
        # 住院号
        self.hospital_no_edit = QLineEdit()
        self.hospital_no_edit.setPlaceholderText('可选')
        self.hospital_no_edit.setMaxLength(20)
        layout.addRow('住院号：', self.hospital_no_edit)
        
        # 治疗开始日期
        self.date_edit = QDateEdit()
        self.date_edit.setCalendarPopup(True)
        self.date_edit.setDate(QDate.currentDate())
        self.date_edit.setDisplayFormat('yyyy-MM-dd')
        layout.addRow('开始日期：', self.date_edit)
        
        return layout
    
    def _create_treatment_content_layout(self):
        """创建治疗选择和内容区域"""
        layout = QVBoxLayout()
        layout.setSpacing(6)
        layout.setContentsMargins(10, 5, 10, 5)
        
        # 治疗项目和诊断 - 使用表单布局
        form_layout = QFormLayout()
        form_layout.setSpacing(6)
        form_layout.setLabelAlignment(Qt.AlignRight | Qt.AlignVCenter)
        
        self.treatment_combo = QComboBox()
        self.treatment_combo.currentIndexChanged.connect(self._on_treatment_changed)
        form_layout.addRow('治疗项目：', self.treatment_combo)
        
        self.diagnosis_combo = QComboBox()
        self.diagnosis_combo.currentIndexChanged.connect(self._on_diagnosis_changed)
        form_layout.addRow('诊断：', self.diagnosis_combo)
        
        layout.addLayout(form_layout)
        
        # 治疗内容 - 可以纵向拉伸
        content_row = QHBoxLayout()
        content_label = QLabel('治疗内容：')
        content_label.setFixedWidth(70)
        content_label.setAlignment(Qt.AlignRight | Qt.AlignTop)
        content_row.addWidget(content_label)
        
        self.content_text = QTextEdit()
        self.content_text.setPlaceholderText('选择治疗项目和诊断后自动填充，可编辑')
        self.content_text.setMinimumHeight(70)
        self.content_text.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        content_row.addWidget(self.content_text)
        
        layout.addLayout(content_row, 1)  # 拉伸因子为1
        
        return layout
    
    def _create_surcharge_group(self):
        """创建加收选项区域"""
        group = QGroupBox('加收选项（仅针灸）')
        layout = QVBoxLayout()
        layout.setSpacing(4)
        layout.setContentsMargins(10, 5, 10, 5)
        
        # 第一行：职称选择
        title_row = QHBoxLayout()
        title_label = QLabel('职称：')
        title_label.setFixedWidth(65)
        title_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        title_row.addWidget(title_label)
        self.title_combo = QComboBox()
        self.title_combo.currentTextChanged.connect(self._on_title_changed)
        self.title_combo.setMinimumWidth(120)
        title_row.addWidget(self.title_combo)
        title_row.addStretch()
        layout.addLayout(title_row)
        
        # 第二、三行：加收项目复选框（分两行）
        self.items_widget = QWidget()
        self.items_layout = QVBoxLayout(self.items_widget)
        self.items_layout.setContentsMargins(0, 0, 0, 0)
        self.items_layout.setSpacing(2)
        self.surcharge_checkboxes = []
        layout.addWidget(self.items_widget)
        
        group.setLayout(layout)
        self.surcharge_group = group
        
        # 加载职称选项
        self._load_titles()
        self._set_surcharge_enabled(False)
        
        return group
    
    def _load_titles(self):
        """加载职称选项"""
        self.title_combo.clear()
        titles = self.config_manager.get_surcharge_titles()
        for title in titles:
            self.title_combo.addItem(title)
    
    def _on_title_changed(self, title):
        """职称改变时更新加收项目选项"""
        # 清除原有复选框和布局
        for cb in self.surcharge_checkboxes:
            cb.deleteLater()
        self.surcharge_checkboxes.clear()
        
        # 清除子布局
        while self.items_layout.count():
            child = self.items_layout.takeAt(0)
            if child.layout():
                # 清除布局中的控件
                while child.layout().count():
                    item = child.layout().takeAt(0)
                    if item.widget():
                        item.widget().deleteLater()
        
        if not title:
            return
        
        # 加载该职称对应的加收项目，分两行显示
        items = self.config_manager.get_surcharge_items_by_title(title)
        
        # 第一行
        row1 = QHBoxLayout()
        label = QLabel('加收项目：')
        label.setFixedWidth(65)
        label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        row1.addWidget(label)
        for i, item in enumerate(items[:2]):
            cb = QCheckBox(item)
            row1.addWidget(cb)
            self.surcharge_checkboxes.append(cb)
        row1.addStretch()
        self.items_layout.addLayout(row1)
        
        # 第二行（如果有）
        if len(items) > 2:
            row2 = QHBoxLayout()
            row2.addSpacing(65)  # 对齐"加收项目："标签
            for item in items[2:]:
                cb = QCheckBox(item)
                row2.addWidget(cb)
                self.surcharge_checkboxes.append(cb)
            row2.addStretch()
            self.items_layout.addLayout(row2)
    
    def _update_surcharge_preview(self):
        """更新加收信息预览（可选实现）"""
        pass
    
    def _create_button_layout(self):
        """创建按钮区域"""
        layout = QHBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(0, 10, 0, 5)
        
        # 设置按钮
        settings_btn = QPushButton('后台设置')
        settings_btn.setFixedWidth(90)
        settings_btn.clicked.connect(self._open_settings)
        layout.addWidget(settings_btn)
        
        layout.addStretch()
        
        # 预览按钮
        preview_btn = QPushButton('预览')
        preview_btn.setFixedWidth(90)
        preview_btn.clicked.connect(self._preview_pdf)
        preview_btn.setDefault(True)
        layout.addWidget(preview_btn)
        
        return layout
    
    def _load_treatments(self):
        """加载治疗项目"""
        self.treatment_combo.clear()
        treatments = self.config_manager.get_treatments()
        
        for treatment in treatments:
            self.treatment_combo.addItem(treatment['name'], treatment['id'])
    
    def _on_treatment_changed(self, index):
        """治疗项目改变时更新诊断列表"""
        if index < 0:
            return
        
        self.current_treatment_id = self.treatment_combo.currentData()
        treatment_name = self.treatment_combo.currentText()
        
        # 判断是否为针灸类治疗，启用/禁用加收选项
        is_acupuncture = self.config_manager.is_acupuncture_treatment(treatment_name)
        self._set_surcharge_enabled(is_acupuncture)
        
        # 如果是针灸类，重新加载加收项目
        if is_acupuncture:
            self._on_title_changed(self.title_combo.currentText())
        
        self._load_diagnoses()
    
    def _set_surcharge_enabled(self, enabled):
        """设置加收区域的启用状态"""
        self.title_combo.setEnabled(enabled)
        for cb in self.surcharge_checkboxes:
            cb.setEnabled(enabled)
            if not enabled:
                cb.setChecked(False)
    
    def _load_diagnoses(self):
        """加载诊断列表"""
        self.diagnosis_combo.clear()
        
        if not self.current_treatment_id:
            return
        
        diagnoses = self.config_manager.get_diagnoses_by_treatment(self.current_treatment_id)
        
        for diag in diagnoses:
            self.diagnosis_combo.addItem(diag['name'], diag['id'])
        
        self._update_content()
    
    def _on_diagnosis_changed(self, index):
        """诊断改变时更新治疗内容"""
        self._update_content()
    
    def _update_content(self):
        """更新治疗内容"""
        treatment_id = self.treatment_combo.currentData()
        diagnosis_id = self.diagnosis_combo.currentData()
        
        if treatment_id and diagnosis_id:
            details = self.config_manager.get_treatment_details(treatment_id, diagnosis_id)
            self.content_text.setPlainText(details)
        else:
            self.content_text.clear()
    
    def _validate_input(self):
        """验证输入"""
        if not self.name_edit.text().strip():
            QMessageBox.warning(self, '提示', '请输入患者姓名')
            return False
        
        if not self.treatment_combo.currentData():
            QMessageBox.warning(self, '提示', '请选择治疗项目')
            return False
        
        if not self.diagnosis_combo.currentData():
            QMessageBox.warning(self, '提示', '请选择诊断')
            return False
        
        return True
    
    def _get_form_data(self):
        """获取表单数据"""
        treatment_id = self.treatment_combo.currentData()
        data = {
            'patient_name': self.name_edit.text().strip(),
            'hospital_no': self.hospital_no_edit.text().strip(),
            'treatment_name': self.treatment_combo.currentText(),
            'diagnosis_name': self.diagnosis_combo.currentText(),
            'treatment_details': self.content_text.toPlainText(),
            'treatment_duration': self.config_manager.get_treatment_duration(treatment_id),
            'start_date': self.date_edit.date().toPyDate(),
            'hospital_name': self.config_manager.get_hospital_name(),
            'surcharge_info': ''
        }
        
        # 加收信息 - 职称 + 选中的加收项目
        if self.title_combo.isEnabled():
            selected_items = []
            for cb in self.surcharge_checkboxes:
                if cb.isChecked():
                    selected_items.append(cb.text())
            
            if selected_items:
                title = self.title_combo.currentText()
                items_str = '、'.join(selected_items)
                data['surcharge_info'] = f'{title}{items_str}'
        
        return data
    
    def _preview_pdf(self):
        """预览PDF"""
        if not self._validate_input():
            return
        
        # 生成临时PDF文件
        temp_path = os.path.join(os.environ.get('TEMP', '.'), '治疗记录单_预览.pdf')
        
        try:
            data = self._get_form_data()
            self.pdf_generator.generate(
                data['patient_name'],
                data['hospital_no'],
                data['diagnosis_name'],
                data['treatment_name'],
                data['treatment_details'],
                data['start_date'],
                temp_path,
                data['hospital_name'],
                data['surcharge_info'],
                data['treatment_duration']
            )
            
            # 打开PDF文件
            os.startfile(temp_path)
            
        except Exception as e:
            QMessageBox.critical(self, '错误', f'生成PDF失败：{str(e)}')
    
    def _open_settings(self):
        """打开后台设置对话框"""
        dialog = SettingsDialog(self, self.config_manager)
        if dialog.exec_():
            # 重新加载治疗项目
            self._load_treatments()
