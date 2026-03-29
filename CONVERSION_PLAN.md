# Python → C# WPF 转换计划

## 项目概览

| 项目 | Python 原版 | C# 目标 |
|------|-------------|---------|
| 框架 | PyQt5 | WPF (.NET 10) |
| PDF库 | reportlab | QuestPDF |
| 配置 | JSON | JSON (System.Text.Json) |
| 打包 | PyInstaller | 单文件发布 |

---

## 转换步骤

### 阶段1: 项目初始化 ✅
- [x] 创建 git 分支 `csharp-rewrite`
- [ ] 创建 WPF 项目结构
- [ ] 配置 NuGet 包依赖

### 阶段2: 数据模型层
- [ ] 创建数据模型类
  - `TreatmentConfig.cs` - 配置根对象
  - `Treatment.cs` - 治疗项目
  - `Diagnosis.cs` - 诊断
  - `Surcharge.cs` - 加收配置

### 阶段3: 服务层
- [ ] `ConfigManager.cs` - 配置管理服务
- [ ] `PdfGenerator.cs` - PDF 生成服务

### 阶段4: UI层
- [ ] `MainWindow.xaml` - 主窗口
- [ ] `SettingsWindow.xaml` - 设置窗口
- [ ] ViewModel 层（MVVM 模式）

### 阶段5: 打包发布
- [ ] 单文件发布配置
- [ ] 测试与优化

---

## 文件映射

```
Python                      →  C#
─────────────────────────────────────────────
main.py                     →  App.xaml + App.xaml.cs
core/config_manager.py      →  Services/ConfigManager.cs
core/pdf_generator.py       →  Services/PdfGenerator.cs
ui/main_window.py           →  Views/MainWindow.xaml + .cs
ui/settings_dialog.py       →  Views/SettingsWindow.xaml + .cs
data/treatment_config.json  →  Config/treatment_config.json
```

---

## 技术要点

### 1. 配置文件路径处理
```csharp
// 开发环境: bin/Debug/net10.0-windows/../../../data/
// 发布后: exe所在目录/data/
string basePath = AppDomain.CurrentDomain.BaseDirectory;
```

### 2. PDF 生成 (QuestPDF)
```csharp
using QuestPDF.Fluent;
using QuestPDF.Helpers;
using QuestPDF.Infrastructure;
```

### 3. MVVM 模式
```csharp
// 使用 CommunityToolkit.Mvvm
[ObservableProperty] private string _hospitalName;
```

---

## 预期效果

| 指标 | Python 版 | C# 版 |
|------|-----------|-------|
| 打包体积 | ~100 MB | 15-25 MB |
| 启动时间 | 3-5 秒 | <1 秒 |
| 内存占用 | 100-200 MB | 30-50 MB |
