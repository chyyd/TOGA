using System;
using System.Collections.Generic;
using System.IO;
using QuestPDF.Fluent;
using QuestPDF.Helpers;
using QuestPDF.Infrastructure;

namespace TreatmentHelper.Services;

/// <summary>
/// PDF生成服务 - 使用QuestPDF生成治疗记录单
/// 精确控制布局确保一页A4可打印
/// </summary>
public class PdfGenerator
{
    private static readonly string[] Weekdays = { "一", "二", "三", "四", "五", "六", "日" };

    static PdfGenerator()
    {
        QuestPDF.Settings.License = LicenseType.Community;
    }

    public string Generate(
        string patientName,
        string hospitalNo,
        string diagnosisName,
        string treatmentName,
        string treatmentDetails,
        DateTime startDate,
        string outputPath,
        string hospitalName = "",
        string surchargeInfo = "",
        string duration = "")
    {
        var document = Document.Create(container =>
        {
            container.Page(page =>
            {
                page.Size(PageSizes.A4);
                page.Margin(10, Unit.Millimetre);
                page.DefaultTextStyle(x => x
                    .FontFamily("SimSun")
                    .FontSize(10)
                    .FontColor(Colors.Black));

                page.Content().Column(col =>
                {
                    // 1. 医院名称
                    if (!string.IsNullOrEmpty(hospitalName))
                    {
                        col.Item().AlignCenter().Text(hospitalName).FontSize(14).Bold();
                        col.Item().Height(3, Unit.Millimetre);
                    }

                    // 2. 标题
                    col.Item().AlignCenter().Text("治疗记录单").FontSize(16).Bold();
                    col.Item().Height(4, Unit.Millimetre);

                    // 3. 患者信息行
                    col.Item().Text(text =>
                    {
                        text.Span("姓名：").Bold();
                        text.Span(patientName);
                        if (!string.IsNullOrEmpty(hospitalNo))
                        {
                            text.Span("    住院号：").Bold();
                            text.Span(hospitalNo);
                        }
                        text.Span("    诊断：").Bold();
                        text.Span(diagnosisName);
                    });
                    col.Item().Height(2, Unit.Millimetre);

                    // 4. 治疗项目行
                    col.Item().Text(text =>
                    {
                        text.Span("治疗项目：").Bold();
                        text.Span(treatmentName);
                        if (!string.IsNullOrEmpty(duration))
                        {
                            text.Span("    时长：").Bold();
                            text.Span(duration);
                        }
                        text.Span("    开始日期：").Bold();
                        text.Span(startDate.ToString("yyyy-MM-dd"));
                    });
                    col.Item().Height(2, Unit.Millimetre);

                    // 5. 治疗内容
                    var content = "治疗内容：" + treatmentDetails;
                    var lines = SplitTextToLines(content, 75);
                    int maxLines = Math.Min(lines.Count, 8);
                    for (int i = 0; i < maxLines; i++)
                    {
                        col.Item().Text(lines[i]).FontSize(10);
                        col.Item().Height(1, Unit.Millimetre);
                    }

                    // 6. 加收信息
                    if (!string.IsNullOrEmpty(surchargeInfo))
                    {
                        col.Item().Text(text =>
                        {
                            text.Span("加收：").Bold();
                            text.Span(surchargeInfo);
                        });
                    }

                    // 7. 表格 - 使用固定高度填满剩余空间
                    col.Item().Height(3, Unit.Millimetre);
                    // A4高度297mm - 上下边距各10mm = 277mm可用
                    // 表格高度 = 277mm - 表头区域(约52mm) = 225mm
                    col.Item().Height(225, Unit.Millimetre).Element(c => DrawTable(c, startDate));
                });
            });
        });

        document.GeneratePdf(outputPath);
        return outputPath;
    }

    private void DrawTable(IContainer container, DateTime startDate)
    {
        container.Table(table =>
        {
            // 3大列，每列等宽
            table.ColumnsDefinition(columns =>
            {
                columns.RelativeColumn();
                columns.RelativeColumn();
                columns.RelativeColumn();
            });

            // 第1列
            table.Cell().Element(c => DrawTableColumn(c, startDate, 0));
            // 第2列
            table.Cell().Element(c => DrawTableColumn(c, startDate, 1));
            // 第3列
            table.Cell().Element(c => DrawTableColumn(c, startDate, 2));
        });
    }

    private void DrawTableColumn(IContainer container, DateTime startDate, int bigCol)
    {
        container.Border(1).Column(col =>
        {
            // 表头行 - 灰色背景，列宽比例：日期18%, 时间28%, 操作者27%, 患者签字27%
            // 转换为相对比例：18:28:27:27 ≈ 2:3:3:3 (简化为整数比)
            col.Item().Background(Colors.Grey.Lighten3).Row(row =>
            {
                row.RelativeItem(2).BorderRight(0.5f).AlignCenter().Padding(2)
                    .Text("日  期").FontSize(8).Bold();
                row.RelativeItem(3).BorderRight(0.5f).AlignCenter().Padding(2)
                    .Text("时  间").FontSize(8).Bold();
                row.RelativeItem(3).BorderRight(0.5f).AlignCenter().Padding(2)
                    .Text("操作者").FontSize(8).Bold();
                row.RelativeItem(3).AlignCenter().Padding(2)
                    .Text("患者签字").FontSize(8).Bold();
            });

            // 20行数据 - 平均分配高度
            for (int row = 0; row < 20; row++)
            {
                int dayOffset = bigCol * 20 + row;
                var currentDate = startDate.AddDays(dayOffset);
                int weekdayIndex = (int)currentDate.DayOfWeek == 0 ? 6 : (int)currentDate.DayOfWeek - 1;
                string dateStr = $"{currentDate.Month}/{currentDate.Day} {Weekdays[weekdayIndex]}";

                col.Item().Extend().BorderBottom(0.5f).Row(dataRow =>
                {
                    dataRow.RelativeItem(2).BorderRight(0.5f).AlignCenter().AlignMiddle()
                        .Text(dateStr).FontSize(7);
                    dataRow.RelativeItem(3).BorderRight(0.5f);
                    dataRow.RelativeItem(3).BorderRight(0.5f);
                    dataRow.RelativeItem(3);
                });
            }
        });
    }

    private List<string> SplitTextToLines(string text, int maxCharsPerLine)
    {
        var lines = new List<string>();
        var paragraphs = text.Split('\n');

        foreach (var para in paragraphs)
        {
            if (string.IsNullOrEmpty(para)) continue;

            var currentLine = "";
            foreach (var ch in para)
            {
                currentLine += ch;
                int width = 0;
                foreach (var c in currentLine)
                {
                    width += c > 127 ? 2 : 1;
                }

                if (width >= maxCharsPerLine)
                {
                    lines.Add(currentLine.TrimEnd());
                    currentLine = "";
                }
            }
            if (!string.IsNullOrEmpty(currentLine))
            {
                lines.Add(currentLine);
            }
        }

        return lines;
    }
}
