# -*- coding: utf-8 -*-
"""配置管理模块"""

import json
import os
import sys

def get_base_dir():
    """获取基础目录，兼容PyInstaller打包"""
    if getattr(sys, 'frozen', False):
        # PyInstaller打包后的路径
        return sys._MEIPASS
    else:
        # 开发环境路径
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

class ConfigManager:
    """管理治疗配置数据"""
    
    def __init__(self, config_path=None):
        if config_path is None:
            base_dir = get_base_dir()
            config_path = os.path.join(base_dir, 'data', 'treatment_config.json')
        self.config_path = config_path
        self.config = self._load_config()
    
    def _load_config(self):
        """加载配置文件"""
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            return {"hospital_name": "", "title": "治疗记录单", "treatments": []}
    
    def save_config(self):
        """保存配置文件"""
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)
    
    def get_hospital_name(self):
        """获取医院名称"""
        return self.config.get('hospital_name', '')
    
    def set_hospital_name(self, name):
        """设置医院名称"""
        self.config['hospital_name'] = name
        self.save_config()
    
    def get_title(self):
        """获取标题"""
        return self.config.get('title', '治疗记录单')
    
    def set_title(self, title):
        """设置标题"""
        self.config['title'] = title
        self.save_config()
    
    def get_treatments(self):
        """获取所有治疗项目"""
        return self.config.get('treatments', [])
    
    def get_treatment_by_id(self, treatment_id):
        """根据ID获取治疗项目"""
        for treatment in self.get_treatments():
            if treatment['id'] == treatment_id:
                return treatment
        return None
    
    def get_treatment_names(self):
        """获取所有治疗项目名称列表"""
        return [t['name'] for t in self.get_treatments()]
    
    def get_diagnoses_by_treatment(self, treatment_id):
        """根据治疗项目ID获取诊断列表"""
        treatment = self.get_treatment_by_id(treatment_id)
        if treatment:
            return treatment.get('diagnoses', [])
        return []
    
    def get_treatment_details(self, treatment_id, diagnosis_id):
        """获取治疗内容"""
        diagnoses = self.get_diagnoses_by_treatment(treatment_id)
        for diag in diagnoses:
            if diag['id'] == diagnosis_id:
                return diag.get('details', '')
        return ''
    
    def add_treatment(self, name):
        """添加治疗项目"""
        treatments = self.get_treatments()
        # 生成新ID
        max_id = 0
        for t in treatments:
            if t['id'].startswith('t'):
                try:
                    num = int(t['id'][1:])
                    if num > max_id:
                        max_id = num
                except ValueError:
                    pass
        new_id = f't{max_id + 1}'
        new_treatment = {
            'id': new_id,
            'name': name,
            'diagnoses': []
        }
        self.config['treatments'].append(new_treatment)
        self.save_config()
        return new_treatment
    
    def update_treatment(self, treatment_id, name):
        """更新治疗项目名称"""
        for treatment in self.config['treatments']:
            if treatment['id'] == treatment_id:
                treatment['name'] = name
                self.save_config()
                return True
        return False
    
    def delete_treatment(self, treatment_id):
        """删除治疗项目"""
        self.config['treatments'] = [
            t for t in self.config['treatments'] if t['id'] != treatment_id
        ]
        self.save_config()
    
    def add_diagnosis(self, treatment_id, name, details=''):
        """添加诊断"""
        treatment = self.get_treatment_by_id(treatment_id)
        if treatment:
            # 生成新ID
            max_id = 0
            for d in treatment.get('diagnoses', []):
                if d['id'].startswith('d'):
                    try:
                        num = int(d['id'][1:])
                        if num > max_id:
                            max_id = num
                    except ValueError:
                        pass
            new_id = f'd{max_id + 1}'
            new_diagnosis = {
                'id': new_id,
                'name': name,
                'details': details
            }
            if 'diagnoses' not in treatment:
                treatment['diagnoses'] = []
            treatment['diagnoses'].append(new_diagnosis)
            self.save_config()
            return new_diagnosis
        return None
    
    def update_diagnosis(self, treatment_id, diagnosis_id, name, details):
        """更新诊断"""
        treatment = self.get_treatment_by_id(treatment_id)
        if treatment:
            for diag in treatment.get('diagnoses', []):
                if diag['id'] == diagnosis_id:
                    diag['name'] = name
                    diag['details'] = details
                    self.save_config()
                    return True
        return False
    
    def delete_diagnosis(self, treatment_id, diagnosis_id):
        """删除诊断"""
        treatment = self.get_treatment_by_id(treatment_id)
        if treatment:
            treatment['diagnoses'] = [
                d for d in treatment.get('diagnoses', []) if d['id'] != diagnosis_id
            ]
            self.save_config()
    
    def get_surcharges(self):
        """获取所有加收配置"""
        return self.config.get('surcharges', [])
    
    def get_surcharge_titles(self):
        """获取加收职称列表"""
        return [s['title'] for s in self.get_surcharges()]
    
    def get_surcharge_by_title(self, title):
        """根据职称获取加收项目"""
        for surcharge in self.get_surcharges():
            if surcharge['title'] == title:
                return surcharge
        return None
    
    def is_acupuncture_treatment(self, treatment_name):
        """判断是否为针灸类治疗项目"""
        return '针灸' in treatment_name
