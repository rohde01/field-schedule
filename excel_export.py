import xlsxwriter

def export_schedule_to_excel(schedule, fields, time_slots):
    # Export schedule to Excel
    workbook = xlsxwriter.Workbook('schedule.xlsx')
    worksheet = workbook.add_worksheet()

    bold_format = workbook.add_format({'bold': True})

    current_col = 0
    worksheet.write(0, current_col, 'Time', bold_format)
    current_col += 1
    for field in fields:
        for subfield in field['subfields']:
            worksheet.write(0, current_col, subfield, bold_format)
            current_col += 1
        worksheet.set_column(current_col, current_col, None)
        current_col += 1

    current_row = 1
    for day in ['Mon', 'Tue', 'Wed', 'Thu', 'Fri']:
        for ts in time_slots:
            if ts.startswith(day):
                current_col = 0
                worksheet.write(current_row, current_col, ts.replace('_', ' '), bold_format)
                current_col += 1
                for field in fields:
                    for subfield in field['subfields']:
                        assignment = schedule[ts][subfield]
                        worksheet.write(current_row, current_col, assignment if assignment else '-')
                        current_col += 1
                    current_col += 1
                current_row += 1
        current_row += 1

    workbook.close()
