# -*- coding: utf-8 -*-
"""后台设置对话框"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout,
    QLabel, QLineEdit, QComboBox, QTextEdit, QPushButton,
    QMessageBox, QListWidget, QListWidgetItem, QGroupBox,
    QSplitter, QFrame
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class SettingsDialog(QDialog):
    """后台设置对话框"""
    
    def __init__(self, parent, config_manager):
        super().__init__(parent)
        self.config_manager = config_manager
        self.current_treatment_id = None
        self.current_diagnosis_id = None
        self.init_ui()
        self._load_settings()
    
    def init_ui(self):
        """初始化界面"""
        self.setWindowTitle('后台设置')
        self.setMinimumSize(700, 500)
        
        layout = QVBoxLayout(self)
        
        # 标题
        title_label = QLabel('后台设置')
        title_label.setFont(QFont('Microsoft YaHei', 14, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # 医院名称设置
        hospital_layout = QHBoxLayout()
        hospital_layout.addWidget(QLabel('医院名称（可选）：'))
        self.hospital_edit = QLineEdit()
        self.hospital_edit.setPlaceholderText('显示在治疗单顶部')
        hospital_layout.addWidget(self.hospital_edit)
        layout.addLayout(hospital_layout)
        
        # 分隔线
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setFrameShadow(QFrame.Sunken)
        layout.addWidget(line)
        
        # 主内容区：左右分割
        splitter = QSplitter(Qt.Horizontal)
        layout.addWidget(splitter)
        
        # 左侧：治疗项目管理
        left_widget = self._create_treatment_panel()
        splitter.addWidget(left_widget)
        
        # 右侧：诊断管理
        right_widget = self._create_diagnosis_panel()
        splitter.addWidget(right_widget)
        
        splitter.setSizes([300, 400])
        
        # 底部按钮
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        save_btn = QPushButton('保存')
        save_btn.clicked.connect(self._save_settings)
        button_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton('取消')
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        layout.addLayout(button_layout)
    
    def _create_treatment_panel(self):
        """创建治疗项目管理面板"""
        group = QGroupBox('治疗项目')
        layout = QVBoxLayout(group)
        
        # 项目列表
        self.treatment_list = QListWidget()
        self.treatment_list.currentItemChanged.connect(self._on_treatment_selected)
        layout.addWidget(self.treatment_list)
        
        # 项目名称编辑
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel('名称：'))
        self.treatment_name_edit = QLineEdit()
        name_layout.addWidget(self.treatment_name_edit)
        layout.addLayout(name_layout)
        
        # 操作按钮
        btn_layout = QHBoxLayout()
        
        add_btn = QPushButton('添加')
        add_btn.clicked.connect(self._add_treatment)
        btn_layout.addWidget(add_btn)
        
        update_btn = QPushButton('更新')
        update_btn.clicked.connect(self._update_treatment)
        btn_layout.addWidget(update_btn)
        
        delete_btn = QPushButton('删除')
        delete_btn.clicked.connect(self._delete_treatment)
        btn_layout.addWidget(delete_btn)
        
        layout.addLayout(btn_layout)
        
        return group
    
    def _create_diagnosis_panel(self):
        """创建诊断管理面板"""
        group = QGroupBox('诊断及治疗内容')
        layout = QVBoxLayout(group)
        
        # 提示
        tip_label = QLabel('请先在左侧选择一个治疗项目')
        tip_label.setStyleSheet('color: gray;')
        layout.addWidget(tip_label)
        
        # 诊断列表
        self.diagnosis_list = QListWidget()
        self.diagnosis_list.currentItemChanged.connect(self._on_diagnosis_selected)
        layout.addWidget(self.diagnosis_list)
        
        # 诊断名称
        name_layout = QHBoxLayout()
        name_layout.addWidget(QLabel('诊断：'))
        self.diagnosis_name_edit = QLineEdit()
        name_layout.addWidget(self.diagnosis_name_edit)
        layout.addLayout(name_layout)
        
        # 治疗内容
        layout.addWidget(QLabel('治疗内容：'))
        self.details_edit = QTextEdit()
        self.details_edit.setPlaceholderText('输入该诊断对应的治疗具体内容')
        layout.addWidget(self.details_edit)
        
        # 操作按钮
        btn_layout = QHBoxLayout()
        
        add_btn = QPushButton('添加')
        add_btn.clicked.connect(self._add_diagnosis)
        btn_layout.addWidget(add_btn)
        
        update_btn = QPushButton('更新')
        update_btn.clicked.connect(self._update_diagnosis)
        btn_layout.addWidget(update_btn)
        
        delete_btn = QPushButton('删除')
        delete_btn.clicked.connect(self._delete_diagnosis)
        btn_layout.addWidget(delete_btn)
        
        layout.addLayout(btn_layout)
        
        return group
    
    def _load_settings(self):
        """加载设置"""
        # 加载医院名称
        self.hospital_edit.setText(self.config_manager.get_hospital_name())
        
        # 加载治疗项目列表
        self._refresh_treatment_list()
    
    def _refresh_treatment_list(self):
        """刷新治疗项目列表"""
        self.treatment_list.clear()
        treatments = self.config_manager.get_treatments()
        
        for treatment in treatments:
            item = QListWidgetItem(treatment['name'])
            item.setData(Qt.UserRole, treatment['id'])
            self.treatment_list.addItem(item)
    
    def _on_treatment_selected(self, current, previous):
        """治疗项目被选中"""
        if current is None:
            self.current_treatment_id = None
            self.diagnosis_list.clear()
            return
        
        self.current_treatment_id = current.data(Qt.UserRole)
        self.treatment_name_edit.setText(current.text())
        
        # 加载该治疗项目下的诊断
        self._refresh_diagnosis_list()
    
    def _refresh_diagnosis_list(self):
        """刷新诊断列表"""
        self.diagnosis_list.clear()
        
        if not self.current_treatment_id:
            return
        
        diagnoses = self.config_manager.get_diagnoses_by_treatment(self.current_treatment_id)
        
        for diag in diagnoses:
            item = QListWidgetItem(diag['name'])
            item.setData(Qt.UserRole, diag['id'])
            self.diagnosis_list.addItem(item)
    
    def _on_diagnosis_selected(self, current, previous):
        """诊断被选中"""
        if current is None:
            self.current_diagnosis_id = None
            self.diagnosis_name_edit.clear()
            self.details_edit.clear()
            return
        
        self.current_diagnosis_id = current.data(Qt.UserRole)
        self.diagnosis_name_edit.setText(current.text())
        
        # 加载治疗内容
        details = self.config_manager.get_treatment_details(
            self.current_treatment_id, self.current_diagnosis_id
        )
        self.details_edit.setPlainText(details)
    
    def _add_treatment(self):
        """添加治疗项目"""
        name = self.treatment_name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, '提示', '请输入治疗项目名称')
            return
        
        self.config_manager.add_treatment(name)
        self._refresh_treatment_list()
        QMessageBox.information(self, '成功', '添加成功')
    
    def _update_treatment(self):
        """更新治疗项目"""
        if not self.current_treatment_id:
            QMessageBox.warning(self, '提示', '请先选择一个治疗项目')
            return
        
        name = self.treatment_name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, '提示', '请输入治疗项目名称')
            return
        
        self.config_manager.update_treatment(self.current_treatment_id, name)
        self._refresh_treatment_list()
        QMessageBox.information(self, '成功', '更新成功')
    
    def _delete_treatment(self):
        """删除治疗项目"""
        if not self.current_treatment_id:
            QMessageBox.warning(self, '提示', '请先选择一个治疗项目')
            return
        
        reply = QMessageBox.question(
            self, '确认', '确定要删除该治疗项目吗？\n这将同时删除该项目的所有诊断信息。',
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.config_manager.delete_treatment(self.current_treatment_id)
            self.current_treatment_id = None
            self._refresh_treatment_list()
            self._refresh_diagnosis_list()
            QMessageBox.information(self, '成功', '删除成功')
    
    def _add_diagnosis(self):
        """添加诊断"""
        if not self.current_treatment_id:
            QMessageBox.warning(self, '提示', '请先选择一个治疗项目')
            return
        
        name = self.diagnosis_name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, '提示', '请输入诊断名称')
            return
        
        details = self.details_edit.toPlainText()
        self.config_manager.add_diagnosis(self.current_treatment_id, name, details)
        self._refresh_diagnosis_list()
        QMessageBox.information(self, '成功', '添加成功')
    
    def _update_diagnosis(self):
        """更新诊断"""
        if not self.current_treatment_id or not self.current_diagnosis_id:
            QMessageBox.warning(self, '提示', '请先选择一个诊断')
            return
        
        name = self.diagnosis_name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, '提示', '请输入诊断名称')
            return
        
        details = self.details_edit.toPlainText()
        self.config_manager.update_diagnosis(
            self.current_treatment_id, self.current_diagnosis_id, name, details
        )
        self._refresh_diagnosis_list()
        QMessageBox.information(self, '成功', '更新成功')
    
    def _delete_diagnosis(self):
        """删除诊断"""
        if not self.current_treatment_id or not self.current_diagnosis_id:
            QMessageBox.warning(self, '提示', '请先选择一个诊断')
            return
        
        reply = QMessageBox.question(
            self, '确认', '确定要删除该诊断吗？',
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.config_manager.delete_diagnosis(
                self.current_treatment_id, self.current_diagnosis_id
            )
            self.current_diagnosis_id = None
            self._refresh_diagnosis_list()
            self.diagnosis_name_edit.clear()
            self.details_edit.clear()
            QMessageBox.information(self, '成功', '删除成功')
    
    def _save_settings(self):
        """保存设置"""
        hospital_name = self.hospital_edit.text().strip()
        self.config_manager.set_hospital_name(hospital_name)
        self.accept()
