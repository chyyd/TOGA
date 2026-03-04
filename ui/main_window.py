# -*- coding: utf-8 -*-
"""主界面模块"""

from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QDateEdit, QComboBox, QTextEdit, QPushButton,
    QMessageBox, QFileDialog, QCheckBox, QGroupBox
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
        self.setMinimumSize(500, 620)
        
        # 创建中心部件
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # 主布局
        main_layout = QVBoxLayout(central_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # 标题
        title_label = QLabel('治疗记录单生成器')
        title_label.setFont(QFont('Microsoft YaHei', 16, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title_label)
        
        # 患者信息区
        info_group = self._create_info_group()
        main_layout.addLayout(info_group)
        
        # 治疗选择区
        treatment_layout = self._create_treatment_layout()
        main_layout.addLayout(treatment_layout)
        
        # 治疗内容区
        content_layout = self._create_content_layout()
        main_layout.addLayout(content_layout)
        
        # 加收选项区
        self.surcharge_group = self._create_surcharge_group()
        main_layout.addWidget(self.surcharge_group)
        
        # 按钮区
        button_layout = self._create_button_layout()
        main_layout.addLayout(button_layout)
        
        # 加载初始数据
        self._load_treatments()
    
    def _create_info_group(self):
        """创建患者信息区域"""
        layout = QFormLayout()
        layout.setSpacing(10)
        
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
        layout.addRow('治疗开始日期：', self.date_edit)
        
        return layout
    
    def _create_treatment_layout(self):
        """创建治疗选择区域"""
        layout = QFormLayout()
        layout.setSpacing(10)
        
        # 治疗项目下拉
        self.treatment_combo = QComboBox()
        self.treatment_combo.currentIndexChanged.connect(self._on_treatment_changed)
        layout.addRow('治疗项目：', self.treatment_combo)
        
        # 诊断下拉
        self.diagnosis_combo = QComboBox()
        self.diagnosis_combo.currentIndexChanged.connect(self._on_diagnosis_changed)
        layout.addRow('诊断：', self.diagnosis_combo)
        
        return layout
    
    def _create_content_layout(self):
        """创建治疗内容区域"""
        layout = QVBoxLayout()
        
        label = QLabel('治疗内容：')
        layout.addWidget(label)
        
        self.content_text = QTextEdit()
        self.content_text.setPlaceholderText('选择治疗项目和诊断后自动填充，可编辑')
        self.content_text.setMaximumHeight(100)
        layout.addWidget(self.content_text)
        
        return layout
    
    def _create_surcharge_group(self):
        """创建加收选项区域"""
        group = QGroupBox('加收选项（仅针灸）')
        layout = QHBoxLayout()
        
        # 启用加收录选框
        self.surcharge_checkbox = QCheckBox('启用加收')
        self.surcharge_checkbox.stateChanged.connect(self._on_surcharge_changed)
        layout.addWidget(self.surcharge_checkbox)
        
        # 操作医师下拉
        layout.addWidget(QLabel('操作医师：'))
        self.doctor_combo = QComboBox()
        self.doctor_combo.setEnabled(False)
        self.doctor_combo.setMinimumWidth(120)
        layout.addWidget(self.doctor_combo)
        
        # 加收信息预览
        self.surcharge_preview = QLabel('')
        self.surcharge_preview.setStyleSheet('color: #666;')
        layout.addWidget(self.surcharge_preview)
        
        layout.addStretch()
        group.setLayout(layout)
        
        # 初始隐藏
        group.setVisible(False)
        
        return group
    
    def _on_surcharge_changed(self, state):
        """加收录选框状态改变"""
        self.doctor_combo.setEnabled(state == Qt.Checked)
        self._update_surcharge_preview()
    
    def _update_surcharge_preview(self):
        """更新加收信息预览"""
        if self.surcharge_checkbox.isChecked():
            doctor_title = self.doctor_combo.currentText()
            surcharge = self.config_manager.get_surcharge_by_title(doctor_title)
            if surcharge:
                items_str = '、'.join(surcharge['items'])
                self.surcharge_preview.setText(f'{doctor_title}{items_str}')
            else:
                self.surcharge_preview.setText('')
        else:
            self.surcharge_preview.setText('')
    
    def _create_button_layout(self):
        """创建按钮区域"""
        layout = QHBoxLayout()
        layout.setSpacing(10)
        
        # 设置按钮
        settings_btn = QPushButton('后台设置')
        settings_btn.clicked.connect(self._open_settings)
        layout.addWidget(settings_btn)
        
        layout.addStretch()
        
        # 预览PDF按钮
        preview_btn = QPushButton('预览PDF')
        preview_btn.clicked.connect(self._preview_pdf)
        layout.addWidget(preview_btn)
        
        # 生成并保存按钮
        generate_btn = QPushButton('生成并保存')
        generate_btn.clicked.connect(self._generate_pdf)
        generate_btn.setDefault(True)
        layout.addWidget(generate_btn)
        
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
        
        # 判断是否为针灸类治疗，显示/隐藏加收选项
        is_acupuncture = self.config_manager.is_acupuncture_treatment(treatment_name)
        self.surcharge_group.setVisible(is_acupuncture)
        
        # 如果是针灸类，加载加收职称
        if is_acupuncture:
            self._load_surcharge_doctors()
        
        self._load_diagnoses()
    
    def _load_surcharge_doctors(self):
        """加载加收职称选项"""
        self.doctor_combo.clear()
        titles = self.config_manager.get_surcharge_titles()
        for title in titles:
            self.doctor_combo.addItem(title)
        
        # 默认选中主任医师
        index = self.doctor_combo.findText('主任医师')
        if index >= 0:
            self.doctor_combo.setCurrentIndex(index)
        
        self._update_surcharge_preview()
    
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
        data = {
            'patient_name': self.name_edit.text().strip(),
            'hospital_no': self.hospital_no_edit.text().strip(),
            'treatment_name': self.treatment_combo.currentText(),
            'diagnosis_name': self.diagnosis_combo.currentText(),
            'treatment_details': self.content_text.toPlainText(),
            'start_date': self.date_edit.date().toPyDate(),
            'hospital_name': self.config_manager.get_hospital_name(),
            'surcharge_info': ''
        }
        
        # 加收信息
        if self.surcharge_checkbox.isChecked() and self.surcharge_group.isVisible():
            doctor_title = self.doctor_combo.currentText()
            surcharge = self.config_manager.get_surcharge_by_title(doctor_title)
            if surcharge:
                items_str = '、'.join(surcharge['items'])
                data['surcharge_info'] = f'{doctor_title}{items_str}'
        
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
                data['surcharge_info']
            )
            
            # 打开PDF文件
            os.startfile(temp_path)
            
        except Exception as e:
            QMessageBox.critical(self, '错误', f'生成PDF失败：{str(e)}')
    
    def _generate_pdf(self):
        """生成并保存PDF"""
        if not self._validate_input():
            return
        
        # 选择保存路径
        default_name = f"治疗记录单_{self.name_edit.text()}_{self.date_edit.date().toString('yyyyMMdd')}.pdf"
        file_path, _ = QFileDialog.getSaveFileName(
            self, '保存PDF', default_name, 'PDF文件 (*.pdf)'
        )
        
        if not file_path:
            return
        
        try:
            data = self._get_form_data()
            self.pdf_generator.generate(
                data['patient_name'],
                data['hospital_no'],
                data['diagnosis_name'],
                data['treatment_name'],
                data['treatment_details'],
                data['start_date'],
                file_path,
                data['hospital_name'],
                data['surcharge_info']
            )
            
            reply = QMessageBox.question(
                self, '成功', 
                f'PDF已保存到：\n{file_path}\n\n是否打开文件？',
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                os.startfile(file_path)
            
        except Exception as e:
            QMessageBox.critical(self, '错误', f'生成PDF失败：{str(e)}')
    
    def _open_settings(self):
        """打开后台设置对话框"""
        dialog = SettingsDialog(self, self.config_manager)
        if dialog.exec_():
            # 重新加载治疗项目
            self._load_treatments()
