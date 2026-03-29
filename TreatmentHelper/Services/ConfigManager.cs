using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text.Json;
using TreatmentHelper.Models;

namespace TreatmentHelper.Services;

/// <summary>
/// 配置管理服务
/// </summary>
public class ConfigManager
{
    private readonly string _configPath;
    private TreatmentConfig _config = new();

    public ConfigManager()
    {
        var baseDir = AppDomain.CurrentDomain.BaseDirectory;
        _configPath = Path.Combine(baseDir, "Config", "treatment_config.json");
        LoadConfig();
    }

    public ConfigManager(string configPath)
    {
        _configPath = configPath;
        LoadConfig();
    }

    private void LoadConfig()
    {
        try
        {
            if (File.Exists(_configPath))
            {
                var json = File.ReadAllText(_configPath);
                _config = JsonSerializer.Deserialize<TreatmentConfig>(json) ?? new TreatmentConfig();
            }
            else
            {
                // 创建默认配置目录
                Directory.CreateDirectory(Path.GetDirectoryName(_configPath)!);
                _config = GetDefaultConfig();
                SaveConfig();
            }
        }
        catch
        {
            _config = new TreatmentConfig();
        }
    }

    private TreatmentConfig GetDefaultConfig()
    {
        return new TreatmentConfig
        {
            HospitalName = "",
            Title = "治疗记录单",
            Surcharges = new List<Surcharge>
            {
                new() { Title = "主任医师", Items = new List<string> { "常规针法加收×1", "特殊手法针法加收×1" } },
                new() { Title = "副主任医师", Items = new List<string> { "常规针法加收×1", "特殊手法针法加收×1" } }
            },
            Treatments = new List<Treatment>()
        };
    }

    public void SaveConfig()
    {
        Directory.CreateDirectory(Path.GetDirectoryName(_configPath)!);
        var options = new JsonSerializerOptions
        {
            WriteIndented = true,
            Encoder = System.Text.Encodings.Web.JavaScriptEncoder.UnsafeRelaxedJsonEscaping
        };
        var json = JsonSerializer.Serialize(_config, options);
        File.WriteAllText(_configPath, json);
    }

    // 医院名称
    public string GetHospitalName() => _config.HospitalName;
    public void SetHospitalName(string name)
    {
        _config.HospitalName = name;
        SaveConfig();
    }

    // 标题
    public string GetTitle() => _config.Title;
    public void SetTitle(string title)
    {
        _config.Title = title;
        SaveConfig();
    }

    // 治疗项目
    public List<Treatment> GetTreatments() => _config.Treatments;

    public Treatment? GetTreatmentById(string id) =>
        _config.Treatments.FirstOrDefault(t => t.Id == id);

    public List<string> GetTreatmentNames() =>
        _config.Treatments.Select(t => t.Name).ToList();

    public string GetTreatmentDuration(string treatmentId)
    {
        var treatment = GetTreatmentById(treatmentId);
        return treatment?.Duration ?? "";
    }

    // 诊断
    public List<Diagnosis> GetDiagnosesByTreatment(string treatmentId)
    {
        var treatment = GetTreatmentById(treatmentId);
        return treatment?.Diagnoses ?? new List<Diagnosis>();
    }

    public string GetTreatmentDetails(string treatmentId, string diagnosisId)
    {
        var diagnoses = GetDiagnosesByTreatment(treatmentId);
        var diag = diagnoses.FirstOrDefault(d => d.Id == diagnosisId);
        return diag?.Details ?? "";
    }

    // 添加治疗项目
    public Treatment AddTreatment(string name, string duration = "")
    {
        var maxId = _config.Treatments
            .Where(t => t.Id.StartsWith("t"))
            .Select(t => int.TryParse(t.Id[1..], out var num) ? num : 0)
            .DefaultIfEmpty(0)
            .Max();

        var newTreatment = new Treatment
        {
            Id = $"t{maxId + 1}",
            Name = name,
            Duration = duration,
            Diagnoses = new List<Diagnosis>()
        };

        _config.Treatments.Add(newTreatment);
        SaveConfig();
        return newTreatment;
    }

    // 更新治疗项目
    public bool UpdateTreatment(string treatmentId, string name, string duration = "")
    {
        var treatment = GetTreatmentById(treatmentId);
        if (treatment == null) return false;

        treatment.Name = name;
        treatment.Duration = duration;
        SaveConfig();
        return true;
    }

    // 删除治疗项目
    public void DeleteTreatment(string treatmentId)
    {
        _config.Treatments.RemoveAll(t => t.Id == treatmentId);
        SaveConfig();
    }

    // 添加诊断
    public Diagnosis? AddDiagnosis(string treatmentId, string name, string details = "")
    {
        var treatment = GetTreatmentById(treatmentId);
        if (treatment == null) return null;

        var maxId = treatment.Diagnoses
            .Where(d => d.Id.StartsWith("d"))
            .Select(d => int.TryParse(d.Id[1..], out var num) ? num : 0)
            .DefaultIfEmpty(0)
            .Max();

        var newDiagnosis = new Diagnosis
        {
            Id = $"d{maxId + 1}",
            Name = name,
            Details = details
        };

        treatment.Diagnoses.Add(newDiagnosis);
        SaveConfig();
        return newDiagnosis;
    }

    // 更新诊断
    public bool UpdateDiagnosis(string treatmentId, string diagnosisId, string name, string details)
    {
        var treatment = GetTreatmentById(treatmentId);
        if (treatment == null) return false;

        var diagnosis = treatment.Diagnoses.FirstOrDefault(d => d.Id == diagnosisId);
        if (diagnosis == null) return false;

        diagnosis.Name = name;
        diagnosis.Details = details;
        SaveConfig();
        return true;
    }

    // 删除诊断
    public void DeleteDiagnosis(string treatmentId, string diagnosisId)
    {
        var treatment = GetTreatmentById(treatmentId);
        if (treatment == null) return;

        treatment.Diagnoses.RemoveAll(d => d.Id == diagnosisId);
        SaveConfig();
    }

    // 加收配置
    public List<Surcharge> GetSurcharges() => _config.Surcharges;

    public List<string> GetSurchargeTitles() =>
        _config.Surcharges.Select(s => s.Title).ToList();

    public List<string> GetSurchargeItemsByTitle(string title)
    {
        var surcharge = _config.Surcharges.FirstOrDefault(s => s.Title == title);
        return surcharge?.Items ?? new List<string>();
    }

    // 判断是否为针灸类治疗
    public bool IsAcupunctureTreatment(string treatmentName) =>
        treatmentName.Contains("针灸");
}
