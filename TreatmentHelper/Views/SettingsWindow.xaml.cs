using System.Windows;
using System.Windows.Controls;
using TreatmentHelper.Models;
using TreatmentHelper.Services;

namespace TreatmentHelper.Views;

/// <summary>
/// SettingsWindow.xaml 的交互逻辑
/// </summary>
public partial class SettingsWindow : Window
{
    private readonly ConfigManager _configManager;
    private string? _currentTreatmentId;
    private string? _currentDiagnosisId;

    public SettingsWindow(ConfigManager configManager)
    {
        InitializeComponent();
        _configManager = configManager;
        LoadSettings();
    }

    private void LoadSettings()
    {
        HospitalNameTextBox.Text = _configManager.GetHospitalName();
        RefreshTreatmentList();
    }

    private void RefreshTreatmentList()
    {
        TreatmentListBox.Items.Clear();
        var treatments = _configManager.GetTreatments();

        foreach (var treatment in treatments)
        {
            TreatmentListBox.Items.Add(new ListBoxItem
            {
                Content = treatment.Name,
                Tag = treatment.Id
            });
        }
    }

    private void RefreshDiagnosisList()
    {
        DiagnosisListBox.Items.Clear();

        if (string.IsNullOrEmpty(_currentTreatmentId))
            return;

        var diagnoses = _configManager.GetDiagnosesByTreatment(_currentTreatmentId);

        foreach (var diag in diagnoses)
        {
            DiagnosisListBox.Items.Add(new ListBoxItem
            {
                Content = diag.Name,
                Tag = diag.Id
            });
        }
    }

    private void TreatmentListBox_SelectionChanged(object sender, SelectionChangedEventArgs e)
    {
        if (TreatmentListBox.SelectedItem is not ListBoxItem item)
        {
            _currentTreatmentId = null;
            DiagnosisListBox.Items.Clear();
            TreatmentNameTextBox.Text = "";
            TreatmentDurationTextBox.Text = "";
            return;
        }

        _currentTreatmentId = item.Tag?.ToString();
        TreatmentNameTextBox.Text = item.Content?.ToString() ?? "";

        // 加载治疗时长
        var duration = _configManager.GetTreatmentDuration(_currentTreatmentId ?? "");
        TreatmentDurationTextBox.Text = duration;

        RefreshDiagnosisList();
    }

    private void DiagnosisListBox_SelectionChanged(object sender, SelectionChangedEventArgs e)
    {
        if (DiagnosisListBox.SelectedItem is not ListBoxItem item)
        {
            _currentDiagnosisId = null;
            DiagnosisNameTextBox.Text = "";
            DetailsTextBox.Text = "";
            return;
        }

        _currentDiagnosisId = item.Tag?.ToString();
        DiagnosisNameTextBox.Text = item.Content?.ToString() ?? "";

        // 加载治疗内容
        var details = _configManager.GetTreatmentDetails(_currentTreatmentId ?? "", _currentDiagnosisId ?? "");
        DetailsTextBox.Text = details;
    }

    private void AddTreatmentButton_Click(object sender, RoutedEventArgs e)
    {
        var name = TreatmentNameTextBox.Text.Trim();
        if (string.IsNullOrEmpty(name))
        {
            MessageBox.Show("请输入治疗项目名称", "提示", MessageBoxButton.OK, MessageBoxImage.Warning);
            return;
        }

        var duration = TreatmentDurationTextBox.Text.Trim();
        _configManager.AddTreatment(name, duration);
        RefreshTreatmentList();
        MessageBox.Show("添加成功", "成功", MessageBoxButton.OK, MessageBoxImage.Information);
    }

    private void UpdateTreatmentButton_Click(object sender, RoutedEventArgs e)
    {
        if (string.IsNullOrEmpty(_currentTreatmentId))
        {
            MessageBox.Show("请先选择一个治疗项目", "提示", MessageBoxButton.OK, MessageBoxImage.Warning);
            return;
        }

        var name = TreatmentNameTextBox.Text.Trim();
        if (string.IsNullOrEmpty(name))
        {
            MessageBox.Show("请输入治疗项目名称", "提示", MessageBoxButton.OK, MessageBoxImage.Warning);
            return;
        }

        var duration = TreatmentDurationTextBox.Text.Trim();
        _configManager.UpdateTreatment(_currentTreatmentId, name, duration);
        RefreshTreatmentList();
        MessageBox.Show("更新成功", "成功", MessageBoxButton.OK, MessageBoxImage.Information);
    }

    private void DeleteTreatmentButton_Click(object sender, RoutedEventArgs e)
    {
        if (string.IsNullOrEmpty(_currentTreatmentId))
        {
            MessageBox.Show("请先选择一个治疗项目", "提示", MessageBoxButton.OK, MessageBoxImage.Warning);
            return;
        }

        var result = MessageBox.Show(
            "确定要删除该治疗项目吗？\n这将同时删除该项目的所有诊断信息。",
            "确认", MessageBoxButton.YesNo, MessageBoxImage.Question);

        if (result == MessageBoxResult.Yes)
        {
            _configManager.DeleteTreatment(_currentTreatmentId);
            _currentTreatmentId = null;
            RefreshTreatmentList();
            RefreshDiagnosisList();
            MessageBox.Show("删除成功", "成功", MessageBoxButton.OK, MessageBoxImage.Information);
        }
    }

    private void AddDiagnosisButton_Click(object sender, RoutedEventArgs e)
    {
        if (string.IsNullOrEmpty(_currentTreatmentId))
        {
            MessageBox.Show("请先选择一个治疗项目", "提示", MessageBoxButton.OK, MessageBoxImage.Warning);
            return;
        }

        var name = DiagnosisNameTextBox.Text.Trim();
        if (string.IsNullOrEmpty(name))
        {
            MessageBox.Show("请输入诊断名称", "提示", MessageBoxButton.OK, MessageBoxImage.Warning);
            return;
        }

        var details = DetailsTextBox.Text;
        _configManager.AddDiagnosis(_currentTreatmentId, name, details);
        RefreshDiagnosisList();
        MessageBox.Show("添加成功", "成功", MessageBoxButton.OK, MessageBoxImage.Information);
    }

    private void UpdateDiagnosisButton_Click(object sender, RoutedEventArgs e)
    {
        if (string.IsNullOrEmpty(_currentTreatmentId) || string.IsNullOrEmpty(_currentDiagnosisId))
        {
            MessageBox.Show("请先选择一个诊断", "提示", MessageBoxButton.OK, MessageBoxImage.Warning);
            return;
        }

        var name = DiagnosisNameTextBox.Text.Trim();
        if (string.IsNullOrEmpty(name))
        {
            MessageBox.Show("请输入诊断名称", "提示", MessageBoxButton.OK, MessageBoxImage.Warning);
            return;
        }

        var details = DetailsTextBox.Text;
        _configManager.UpdateDiagnosis(_currentTreatmentId, _currentDiagnosisId, name, details);
        RefreshDiagnosisList();
        MessageBox.Show("更新成功", "成功", MessageBoxButton.OK, MessageBoxImage.Information);
    }

    private void DeleteDiagnosisButton_Click(object sender, RoutedEventArgs e)
    {
        if (string.IsNullOrEmpty(_currentTreatmentId) || string.IsNullOrEmpty(_currentDiagnosisId))
        {
            MessageBox.Show("请先选择一个诊断", "提示", MessageBoxButton.OK, MessageBoxImage.Warning);
            return;
        }

        var result = MessageBox.Show(
            "确定要删除该诊断吗？",
            "确认", MessageBoxButton.YesNo, MessageBoxImage.Question);

        if (result == MessageBoxResult.Yes)
        {
            _configManager.DeleteDiagnosis(_currentTreatmentId, _currentDiagnosisId);
            _currentDiagnosisId = null;
            RefreshDiagnosisList();
            DiagnosisNameTextBox.Text = "";
            DetailsTextBox.Text = "";
            MessageBox.Show("删除成功", "成功", MessageBoxButton.OK, MessageBoxImage.Information);
        }
    }

    private void SaveButton_Click(object sender, RoutedEventArgs e)
    {
        var hospitalName = HospitalNameTextBox.Text.Trim();
        _configManager.SetHospitalName(hospitalName);
        DialogResult = true;
        Close();
    }

    private void CancelButton_Click(object sender, RoutedEventArgs e)
    {
        DialogResult = false;
        Close();
    }
}
