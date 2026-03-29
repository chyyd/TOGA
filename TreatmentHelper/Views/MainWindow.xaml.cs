using System;
using System.Collections.Generic;
using System.IO;
using System.Windows;
using System.Windows.Controls;
using TreatmentHelper.Services;

namespace TreatmentHelper.Views;

/// <summary>
/// MainWindow.xaml 的交互逻辑
/// </summary>
public partial class MainWindow : Window
{
    private readonly ConfigManager _configManager;
    private readonly PdfGenerator _pdfGenerator;
    private string? _currentTreatmentId;

    public MainWindow()
    {
        InitializeComponent();
        _configManager = new ConfigManager();
        _pdfGenerator = new PdfGenerator();

        // 初始化日期选择器
        StartDatePicker.SelectedDate = DateTime.Today;

        // 加载数据
        LoadTreatments();
        LoadTitles();
        SetSurchargeEnabled(false);
    }

    private void LoadTreatments()
    {
        TreatmentComboBox.Items.Clear();
        var treatments = _configManager.GetTreatments();

        foreach (var treatment in treatments)
        {
            TreatmentComboBox.Items.Add(new ComboBoxItem
            {
                Content = treatment.Name,
                Tag = treatment.Id
            });
        }

        if (TreatmentComboBox.Items.Count > 0)
            TreatmentComboBox.SelectedIndex = 0;
    }

    private void LoadDiagnoses()
    {
        DiagnosisComboBox.Items.Clear();

        if (string.IsNullOrEmpty(_currentTreatmentId))
            return;

        var diagnoses = _configManager.GetDiagnosesByTreatment(_currentTreatmentId);

        foreach (var diag in diagnoses)
        {
            DiagnosisComboBox.Items.Add(new ComboBoxItem
            {
                Content = diag.Name,
                Tag = diag.Id
            });
        }

        if (DiagnosisComboBox.Items.Count > 0)
            DiagnosisComboBox.SelectedIndex = 0;
    }

    private void LoadTitles()
    {
        TitleComboBox.Items.Clear();
        var titles = _configManager.GetSurchargeTitles();

        foreach (var title in titles)
        {
            TitleComboBox.Items.Add(title);
        }

        if (TitleComboBox.Items.Count > 0)
            TitleComboBox.SelectedIndex = 0;
    }

    private void LoadSurchargeItems(string title)
    {
        // 清除两行的复选框
        ItemsRow1Panel.Children.Clear();
        ItemsRow2Panel.Children.Clear();

        if (string.IsNullOrEmpty(title))
            return;

        var items = _configManager.GetSurchargeItemsByTitle(title);
        var isEnabled = SurchargeGroupBox.IsEnabled;

        // 前2个放第一行
        for (int i = 0; i < Math.Min(2, items.Count); i++)
        {
            var checkBox = new CheckBox
            {
                Content = items[i],
                Margin = new Thickness(5, 0, 15, 0),
                IsEnabled = isEnabled
            };
            ItemsRow1Panel.Children.Add(checkBox);
        }

        // 后面的放第二行
        for (int i = 2; i < items.Count; i++)
        {
            var checkBox = new CheckBox
            {
                Content = items[i],
                Margin = new Thickness(5, 0, 15, 0),
                IsEnabled = isEnabled
            };
            ItemsRow2Panel.Children.Add(checkBox);
        }
    }

    private void TreatmentComboBox_SelectionChanged(object sender, SelectionChangedEventArgs e)
    {
        if (TreatmentComboBox.SelectedItem is not ComboBoxItem item)
            return;

        _currentTreatmentId = item.Tag?.ToString();
        var treatmentName = item.Content?.ToString() ?? "";

        // 判断是否为针灸类治疗
        var isAcupuncture = _configManager.IsAcupunctureTreatment(treatmentName);
        SetSurchargeEnabled(isAcupuncture);

        if (isAcupuncture && TitleComboBox.SelectedItem is string title)
        {
            LoadSurchargeItems(title);
        }

        LoadDiagnoses();
    }

    private void DiagnosisComboBox_SelectionChanged(object sender, SelectionChangedEventArgs e)
    {
        UpdateContent();
    }

    private void TitleComboBox_SelectionChanged(object sender, SelectionChangedEventArgs e)
    {
        if (TitleComboBox.SelectedItem is string title)
        {
            LoadSurchargeItems(title);
        }
    }

    private void UpdateContent()
    {
        if (TreatmentComboBox.SelectedItem is not ComboBoxItem treatmentItem ||
            DiagnosisComboBox.SelectedItem is not ComboBoxItem diagnosisItem)
        {
            ContentTextBox.Text = "";
            return;
        }

        var treatmentId = treatmentItem.Tag?.ToString();
        var diagnosisId = diagnosisItem.Tag?.ToString();

        if (!string.IsNullOrEmpty(treatmentId) && !string.IsNullOrEmpty(diagnosisId))
        {
            var details = _configManager.GetTreatmentDetails(treatmentId, diagnosisId);
            ContentTextBox.Text = details;
        }
        else
        {
            ContentTextBox.Text = "";
        }
    }

    private void SetSurchargeEnabled(bool enabled)
    {
        SurchargeGroupBox.IsEnabled = enabled;

        // 取消选中所有复选框
        if (!enabled)
        {
            foreach (var child in ItemsRow1Panel.Children)
            {
                if (child is CheckBox checkBox)
                    checkBox.IsChecked = false;
            }
            foreach (var child in ItemsRow2Panel.Children)
            {
                if (child is CheckBox checkBox)
                    checkBox.IsChecked = false;
            }
        }
    }

    private bool ValidateInput()
    {
        if (string.IsNullOrWhiteSpace(NameTextBox.Text))
        {
            MessageBox.Show("请输入患者姓名", "提示", MessageBoxButton.OK, MessageBoxImage.Warning);
            NameTextBox.Focus();
            return false;
        }

        if (TreatmentComboBox.SelectedItem == null)
        {
            MessageBox.Show("请选择治疗项目", "提示", MessageBoxButton.OK, MessageBoxImage.Warning);
            return false;
        }

        if (DiagnosisComboBox.SelectedItem == null)
        {
            MessageBox.Show("请选择诊断", "提示", MessageBoxButton.OK, MessageBoxImage.Warning);
            return false;
        }

        return true;
    }

    private (string patientName, string hospitalNo, string diagnosisName, string treatmentName,
            string treatmentDetails, DateTime startDate, string hospitalName,
            string surchargeInfo, string duration) GetFormData()
    {
        var treatmentItem = (ComboBoxItem)TreatmentComboBox.SelectedItem;
        var diagnosisItem = (ComboBoxItem)DiagnosisComboBox.SelectedItem;
        var treatmentId = treatmentItem.Tag?.ToString() ?? "";

        // 获取加收信息 - 从两行收集
        var surchargeInfo = "";
        if (SurchargeGroupBox.IsEnabled && TitleComboBox.SelectedItem is string title)
        {
            var selectedItems = new List<string>();
            
            foreach (var child in ItemsRow1Panel.Children)
            {
                if (child is CheckBox { IsChecked: true } checkBox)
                    selectedItems.Add(checkBox.Content?.ToString() ?? "");
            }
            foreach (var child in ItemsRow2Panel.Children)
            {
                if (child is CheckBox { IsChecked: true } checkBox)
                    selectedItems.Add(checkBox.Content?.ToString() ?? "");
            }

            if (selectedItems.Count > 0)
            {
                surchargeInfo = $"{title}{string.Join("、", selectedItems)}";
            }
        }

        return (
            NameTextBox.Text.Trim(),
            HospitalNoTextBox.Text.Trim(),
            diagnosisItem.Content?.ToString() ?? "",
            treatmentItem.Content?.ToString() ?? "",
            ContentTextBox.Text,
            StartDatePicker.SelectedDate ?? DateTime.Today,
            _configManager.GetHospitalName(),
            surchargeInfo,
            _configManager.GetTreatmentDuration(treatmentId)
        );
    }

    private void PreviewButton_Click(object sender, RoutedEventArgs e)
    {
        if (!ValidateInput())
            return;

        try
        {
            var data = GetFormData();
            var tempPath = Path.Combine(Path.GetTempPath(), "治疗记录单_预览.pdf");

            _pdfGenerator.Generate(
                data.patientName,
                data.hospitalNo,
                data.diagnosisName,
                data.treatmentName,
                data.treatmentDetails,
                data.startDate,
                tempPath,
                data.hospitalName,
                data.surchargeInfo,
                data.duration
            );

            // 打开PDF文件
            System.Diagnostics.Process.Start(new System.Diagnostics.ProcessStartInfo
            {
                FileName = tempPath,
                UseShellExecute = true
            });
        }
        catch (Exception ex)
        {
            MessageBox.Show($"生成PDF失败：{ex.Message}", "错误", MessageBoxButton.OK, MessageBoxImage.Error);
        }
    }

    private void SettingsButton_Click(object sender, RoutedEventArgs e)
    {
        var settingsWindow = new SettingsWindow(_configManager);
        if (settingsWindow.ShowDialog() == true)
        {
            // 重新加载治疗项目
            LoadTreatments();
        }
    }
}
