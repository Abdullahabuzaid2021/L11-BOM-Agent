import openpyxl

wb = openpyxl.load_workbook('BOM_CONSOLIDATED_FINAL_WITH_SECTIONS.xlsx')
ws = wb.active

print('Rows 5-8 values:')
for row_num in range(5, 9):
    print(f'\nRow {row_num}:')
    for col_num, cell in enumerate(ws[row_num]):
        print(f'  Column {col_num}: {cell.value}')
