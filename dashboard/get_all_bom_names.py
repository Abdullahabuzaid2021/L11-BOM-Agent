import openpyxl

wb = openpyxl.load_workbook('BOM_CONSOLIDATED_FINAL_WITH_SECTIONS.xlsx')
ws = wb.active

print('All BOM filenames in row 1:')
for col in range(1, 30):
    cell = ws.cell(row=1, column=col)
    if cell.value:
        print(f'Column {col}: {cell.value}')
