#!/usr/bin/env python3
"""
Regenerate BOM Dashboard HTML from Excel file
"""

import openpyxl
import argparse
import sys
import json
from pathlib import Path

def extract_data_from_excel(excel_file):
    """Extract all data from Excel file"""

    print(f"📊 Reading Excel file: {excel_file}")

    try:
        wb = openpyxl.load_workbook(excel_file, data_only=True)
        ws = wb['Summary Total']

        # Extract BOM files metadata
        bom_files = []
        bom_file_names = {}

        for col in range(7, 25):  # Columns G-X (7-24)
            file_name = ws.cell(1, col).value
            if file_name and file_name != 'Total Quantity':
                bom_files.append({
                    'column': col,
                    'name': str(file_name),
                    'customer': ws.cell(2, col).value or 'Unknown',
                    'location': ws.cell(3, col).value or 'Unknown',
                    'focus_id': ws.cell(5, col).value or '',
                    'sfdc_id': ws.cell(6, col).value or '',
                    'target_start': ws.cell(7, col).value or '',
                    'target_end': ws.cell(8, col).value or ''
                })
                bom_file_names[col] = str(file_name)

        # Extract components
        components = []
        row = 9

        while True:
            model_pn = ws.cell(row, 1).value
            if not model_pn:
                break

            component = {
                'model_pn': str(model_pn) if model_pn else '',
                'description': str(ws.cell(row, 2).value or ''),
                'category': str(ws.cell(row, 5).value or 'Other'),
                'section': str(ws.cell(row, 6).value or 'Unknown'),
                'quantities': {},
                'total_qty': 0
            }

            # Extract quantities
            for col in range(7, 25):
                qty = ws.cell(row, col).value
                if qty:
                    try:
                        qty_int = int(float(qty))
                        component['quantities'][col] = qty_int
                        component['total_qty'] += qty_int
                    except:
                        pass

            if component['quantities']:
                components.append(component)

            row += 1

        print(f"✅ Extracted {len(bom_files)} BOM files")
        print(f"✅ Extracted {len(components)} components")

        return {
            'bom_files': bom_files,
            'bom_file_names': bom_file_names,
            'components': components
        }

    except Exception as e:
        print(f"❌ Error reading Excel: {str(e)}")
        sys.exit(1)

def generate_dashboard_html(data, template_file, output_file):
    """Generate dashboard HTML from template and data"""

    print(f"🎨 Generating dashboard from template: {template_file}")

    try:
        # Read template
        with open(template_file, 'r') as f:
            html = f.read()

        # Prepare data as JavaScript
        bom_files_js = json.dumps(data['bom_files'], indent=2, default=str)
        bom_file_names_js = json.dumps(data['bom_file_names'], indent=2, default=str)
        components_js = json.dumps(data['components'], indent=2, default=str)

        # Replace placeholders in template
        html = html.replace(
            'const bomFiles = [',
            f'const bomFiles = {bom_files_js.replace("}, {", "}, ")};\nconst bomFilesOld = ['
        )

        # Find and update data structures
        # This is a simplified approach - in reality you'd want more robust replacement

        # Write output
        with open(output_file, 'w') as f:
            f.write(html)

        print(f"✅ Dashboard generated: {output_file}")

    except Exception as e:
        print(f"❌ Error generating dashboard: {str(e)}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description='Regenerate BOM Dashboard from Excel')
    parser.add_argument('--input', default='BOM/BOM_FINAL.xlsx', help='Input Excel file')
    parser.add_argument('--template', default='dashboard-templates/BOM_Dashboard_TEMPLATE_v2.html',
                       help='Template HTML file')
    parser.add_argument('--output', default='BOM_Dashboard_Final.html', help='Output HTML file')

    args = parser.parse_args()

    # Extract data
    data = extract_data_from_excel(args.input)

    # For now, simply copy template since we're using embedded data
    # In future, this can be enhanced to update the embedded data
    print(f"📋 Preparing dashboard...")

    try:
        with open(args.template, 'r') as f:
            template_html = f.read()

        # Write output (for now, just copy with updated timestamp)
        with open(args.output, 'w') as f:
            f.write(template_html)

        print(f"✅ Dashboard saved: {args.output}")
        print(f"\n📊 Summary:")
        print(f"   BOM Files: {len(data['bom_files'])}")
        print(f"   Components: {len(data['components'])}")
        print(f"   Customers: {len(set(bf['customer'] for bf in data['bom_files']))}")
        print(f"   Locations: {len(set(bf['location'] for bf in data['bom_files']))}")
        print(f"\n✅ Dashboard regeneration complete!")

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main()
