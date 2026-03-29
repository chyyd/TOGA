using System;
using System.Collections.Generic;
using System.IO;
using QuestPDF.Fluent;
using QuestPDF.Helpers;
using QuestPDF.Infrastructure;

namespace TreatmentHelper.Services;

/// <summary>
/// PDF生成服务 - 动态计算行高，填满剩余空间
/// </summary>
public class PdfGenerator
{
    private static readonly string[] Weekdays = { "一", "二", "三", "四", "五", "六", "日" };
    private const float PageWidthMm = 210f;
    private const float PageHeightMm = 297f;
    private const float MarginMm = 10f;
    private const float LeftIndentMm = 5f;  // 文字左边缩进（对应Python的15mm从左边距算起）

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
                page.Margin(MarginMm, Unit.Millimetre);
                page.DefaultTextStyle(x => x
                    .FontFamily("SimSun")
                    .FontSize(10)
                    .FontColor(Colors.Black));

                page.Content().Column(col =>
                {
                    // 1. 医院名称
                    float currentY = MarginMm;
                    if (!string.IsNullOrEmpty(hospitalName))
                    {
                        col.Item().AlignCenter().Text(hospitalName).FontSize(14).Bold();
                        currentY += 7;
                    }

                    // 2. 标题
                    col.Item().AlignCenter().Text("治疗记录单").FontSize(16).Bold();
                    currentY += 8;

                    // 3. 患者信息行
                    col.Item().PaddingLeft(LeftIndentMm, Unit.Millimetre).Text(text =>
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
                    col.Item().Height(1.5f, Unit.Millimetre);
                    currentY += 7.5f;

                    // 4. 治疗项目行
                    col.Item().PaddingLeft(LeftIndentMm, Unit.Millimetre).Text(text =>
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
                    col.Item().Height(1.5f, Unit.Millimetre);
                    currentY += 7.5f;

                    // 5. 治疗内容 - 使用95mm宽度（210-35=175mm）
                    var content = "治疗内容：" + treatmentDetails;
                    var lines = SplitTextToLines(content, 95);
                    int maxLines = Math.Min(lines.Count, 8);
                    for (int i = 0; i < maxLines; i++)
                    {
                        col.Item().PaddingLeft(LeftIndentMm, Unit.Millimetre).Text(lines[i]).FontSize(10);
                        col.Item().Height(1.5f, Unit.Millimetre);
                        currentY += 6f;
                    }

                    // 6. 加收信息
                    if (!string.IsNullOrEmpty(surchargeInfo))
                    {
                        col.Item().PaddingLeft(LeftIndentMm, Unit.Millimetre).Text(text =>
                        {
                            text.Span("加收：").Bold();
                            text.Span(surchargeInfo);
                        });
                        col.Item().Height(1.5f, Unit.Millimetre);
                        currentY += 6f;
                    }

                    // 7. 表格 - 动态计算行高
                    currentY += 3; // 表格前的间距
                    float availableHeight = PageHeightMm - MarginMm - currentY; // 剩余可用高度
                    int tableRows = 21; // 1表头 + 20数据
                    float rowHeight = availableHeight / tableRows;

                    col.Item().Element(c => DrawTable(c, startDate, availableHeight, rowHeight));
                });
            });
        });

        document.GeneratePdf(outputPath);
        return outputPath;
    }

    private void DrawTable(IContainer container, DateTime startDate, float tableHeight, float rowHeight)
    {
        container.Height(tableHeight, Unit.Millimetre).Table(table =>
        {
            // 12列：3个大列，每个大列4个小列 (18:28:27:27 比例)
            table.ColumnsDefinition(columns =>
            {
                // 第1大列
                columns.RelativeColumn(18);
                columns.RelativeColumn(28);
                columns.RelativeColumn(27);
                columns.RelativeColumn(27);
                // 第2大列
                columns.RelativeColumn(18);
                columns.RelativeColumn(28);
                columns.RelativeColumn(27);
                columns.RelativeColumn(27);
                // 第3大列
                columns.RelativeColumn(18);
                columns.RelativeColumn(28);
                columns.RelativeColumn(27);
                columns.RelativeColumn(27);
            });

            // 表头行
            for (int bigCol = 0; bigCol < 3; bigCol++)
            {
                table.Cell().Border(0.5f).Height(rowHeight, Unit.Millimetre).Background(Colors.Grey.Lighten3)
                    .AlignCenter().AlignMiddle().Text("日  期").FontSize(8).Bold();
                table.Cell().Border(0.5f).Height(rowHeight, Unit.Millimetre).Background(Colors.Grey.Lighten3)
                    .AlignCenter().AlignMiddle().Text("时  间").FontSize(8).Bold();
                table.Cell().Border(0.5f).Height(rowHeight, Unit.Millimetre).Background(Colors.Grey.Lighten3)
                    .AlignCenter().AlignMiddle().Text("操作者").FontSize(8).Bold();
                table.Cell().Border(0.5f).Height(rowHeight, Unit.Millimetre).Background(Colors.Grey.Lighten3)
                    .AlignCenter().AlignMiddle().Text("患者签字").FontSize(8).Bold();
            }

            // 20行数据
            for (int row = 0; row < 20; row++)
            {
                for (int bigCol = 0; bigCol < 3; bigCol++)
                {
                    int dayOffset = bigCol * 20 + row;
                    var currentDate = startDate.AddDays(dayOffset);
                    int weekdayIndex = (int)currentDate.DayOfWeek == 0 ? 6 : (int)currentDate.DayOfWeek - 1;
                    string dateStr = $"{currentDate.Month}/{currentDate.Day} {Weekdays[weekdayIndex]}";

                    // 日期
                    table.Cell().Border(0.5f).Height(rowHeight, Unit.Millimetre)
                        .AlignCenter().AlignMiddle().Text(dateStr).FontSize(7);
                    // 时间 (空)
                    table.Cell().Border(0.5f).Height(rowHeight, Unit.Millimetre);
                    // 操作者 (空)
                    table.Cell().Border(0.5f).Height(rowHeight, Unit.Millimetre);
                    // 患者签字 (空)
                    table.Cell().Border(0.5f).Height(rowHeight, Unit.Millimetre);
                }
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
