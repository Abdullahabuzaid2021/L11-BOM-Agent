import openpyxl

wb = openpyxl.load_workbook('BOM_CONSOLIDATED_FINAL_WITH_SECTIONS.xlsx')
ws = wb.active

print('Searching for "# of bldg" row:')
for row_num in range(1, 20):
    cell = ws.cell(row=row_num, column=1)
    if cell.value and 'bldg' in str(cell.value).lower():
        print(f'Row {row_num}: {cell.value}')
