using System;
using System.Collections.Generic;
using System.IO;
using QuestPDF.Fluent;
using QuestPDF.Helpers;
using QuestPDF.Infrastructure;

namespace TreatmentHelper.Services;

/// <summary>
/// PDF生成服务 - 使用QuestPDF生成治疗记录单
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
                    DrawHeader(col, hospitalName, patientName, hospitalNo, 
                        diagnosisName, treatmentName, startDate, duration);
                    DrawTreatmentDetails(col, treatmentDetails);

                    if (!string.IsNullOrEmpty(surchargeInfo))
                    {
                        DrawSurcharge(col, surchargeInfo);
                    }

                    col.Item().PaddingTop(3, Unit.Millimetre);
                    DrawTable(col, startDate);
                });
            });
        });

        document.GeneratePdf(outputPath);
        return outputPath;
    }

    private void DrawHeader(ColumnDescriptor col, string hospitalName, string patientName,
        string hospitalNo, string diagnosisName, string treatmentName,
        DateTime startDate, string duration)
    {
        if (!string.IsNullOrEmpty(hospitalName))
        {
            col.Item().AlignCenter().Text(hospitalName).FontSize(14).Bold();
            col.Item().PaddingVertical(3, Unit.Millimetre);
        }

        col.Item().AlignCenter().Text("治疗记录单").FontSize(16).Bold();
        col.Item().PaddingVertical(4, Unit.Millimetre);

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
        col.Item().PaddingVertical(2, Unit.Millimetre);

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
        col.Item().PaddingVertical(2, Unit.Millimetre);
    }

    private void DrawTreatmentDetails(ColumnDescriptor col, string treatmentDetails)
    {
        var content = "治疗内容：" + treatmentDetails;
        var lines = SplitTextToLines(content, 85);
        var maxLines = Math.Min(lines.Count, 8);

        for (int i = 0; i < maxLines; i++)
        {
            col.Item().Text(lines[i]).FontSize(10);
            col.Item().PaddingVertical(1, Unit.Millimetre);
        }
    }

    private void DrawSurcharge(ColumnDescriptor col, string surchargeInfo)
    {
        col.Item().PaddingTop(2, Unit.Millimetre);
        col.Item().Text(text =>
        {
            text.Span("加收：").Bold();
            text.Span(surchargeInfo);
        });
    }

    private void DrawTable(ColumnDescriptor col, DateTime startDate)
    {
        col.Item().Table(table =>
        {
            table.ColumnsDefinition(columns =>
            {
                columns.RelativeColumn();
                columns.RelativeColumn();
                columns.RelativeColumn();
            });

            // 第1列
            table.Cell().Column(1).Element(c => DrawTableColumn(c, startDate, 0));
            // 第2列
            table.Cell().Column(2).Element(c => DrawTableColumn(c, startDate, 1));
            // 第3列
            table.Cell().Column(3).Element(c => DrawTableColumn(c, startDate, 2));
        });
    }

    private void DrawTableColumn(IContainer container, DateTime startDate, int bigCol)
    {
        container.Border(1).Column(col =>
        {
            // 表头行
            col.Item().Border(1).Background(Colors.Grey.Lighten3).Row(row =>
            {
                row.RelativeItem().BorderRight(0.5f).AlignCenter().Padding(2)
                    .Text("日  期").FontSize(8).Bold();
                row.RelativeItem().BorderRight(0.5f).AlignCenter().Padding(2)
                    .Text("时  间").FontSize(8).Bold();
                row.RelativeItem().BorderRight(0.5f).AlignCenter().Padding(2)
                    .Text("操作者").FontSize(8).Bold();
                row.RelativeItem().AlignCenter().Padding(2)
                    .Text("患者签字").FontSize(8).Bold();
            });

            // 20行数据
            for (int row = 0; row < 20; row++)
            {
                int dayOffset = bigCol * 20 + row;
                var currentDate = startDate.AddDays(dayOffset);
                var weekday = Weekdays[(int)currentDate.DayOfWeek == 0 ? 6 : (int)currentDate.DayOfWeek - 1];
                var dateStr = $"{currentDate.Month}/{currentDate.Day} {weekday}";

                col.Item().BorderLeft(0.5f).BorderRight(0.5f).BorderBottom(0.5f)
                    .Height(12, Unit.Millimetre).Row(dataRow =>
                    {
                        dataRow.RelativeItem().BorderRight(0.5f).AlignCenter()
                            .Text(dateStr).FontSize(7);
                        dataRow.RelativeItem().BorderRight(0.5f);
                        dataRow.RelativeItem().BorderRight(0.5f);
                        dataRow.RelativeItem();
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
