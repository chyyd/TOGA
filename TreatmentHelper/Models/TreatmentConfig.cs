using System.Collections.Generic;
using System.Text.Json.Serialization;

namespace TreatmentHelper.Models;

/// <summary>
/// 治疗配置根对象
/// </summary>
public class TreatmentConfig
{
    [JsonPropertyName("hospital_name")]
    public string HospitalName { get; set; } = "";

    [JsonPropertyName("title")]
    public string Title { get; set; } = "治疗记录单";

    [JsonPropertyName("surcharges")]
    public List<Surcharge> Surcharges { get; set; } = new();

    [JsonPropertyName("treatments")]
    public List<Treatment> Treatments { get; set; } = new();
}

/// <summary>
/// 治疗项目
/// </summary>
public class Treatment
{
    [JsonPropertyName("id")]
    public string Id { get; set; } = "";

    [JsonPropertyName("name")]
    public string Name { get; set; } = "";

    [JsonPropertyName("duration")]
    public string Duration { get; set; } = "";

    [JsonPropertyName("diagnoses")]
    public List<Diagnosis> Diagnoses { get; set; } = new();
}

/// <summary>
/// 诊断
/// </summary>
public class Diagnosis
{
    [JsonPropertyName("id")]
    public string Id { get; set; } = "";

    [JsonPropertyName("name")]
    public string Name { get; set; } = "";

    [JsonPropertyName("details")]
    public string Details { get; set; } = "";
}

/// <summary>
/// 加收配置
/// </summary>
public class Surcharge
{
    [JsonPropertyName("title")]
    public string Title { get; set; } = "";

    [JsonPropertyName("items")]
    public List<string> Items { get; set; } = new();
}
