# TOGA - Treatment Order Generation Assistant

治疗记录单生成器 - 针灸康复治疗单自动生成工具

## 功能特点

- 快速生成90天治疗记录单（A4纸，3列×30行）
- 支持多种治疗项目：针灸、针灸+红外线、推拿、中频电疗、康复训练等
- 治疗项目-诊断-治疗内容三级对应关系，后台可维护
- 自动计算日期和星期
- 支持PDF预览、保存、打印

## 安装

```bash
pip install -r requirements.txt
```

## 使用

```bash
python main.py
```

## 界面说明

### 主界面

1. 填写患者信息（姓名必填，住院号可选）
2. 选择治疗开始日期（默认当天）
3. 选择治疗项目（下拉菜单）
4. 选择诊断（根据治疗项目自动匹配）
5. 治疗内容自动填充，可手动编辑
6. 点击"预览PDF"或"生成并保存"

### 后台设置

点击"后台设置"按钮可维护：
- 医院名称（显示在治疗单顶部）
- 治疗项目
- 诊断及对应的治疗内容

## 项目结构

```
TOGA/
├── main.py                 # 程序入口
├── requirements.txt        # 依赖
├── ui/
│   ├── main_window.py      # 主界面
│   └── settings_dialog.py  # 后台设置
├── core/
│   ├── config_manager.py   # 配置管理
│   └── pdf_generator.py    # PDF生成
└── data/
    └── treatment_config.json  # 三级关系数据
```

## 技术栈

- **GUI**: PyQt5
- **PDF生成**: ReportLab
- **数据存储**: JSON

## 许可证

MIT License
