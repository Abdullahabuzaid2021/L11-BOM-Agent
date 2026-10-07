"""
BOM Consolidation Merge V2 - Enhanced with rack consolidation and item mappings
"""
from pathlib import Path
import openpyxl
from collections import defaultdict
import sys
import copy

sys.path.insert(0, str(Path.cwd()))
from BOM_CONSOLIDATION_FINAL_SOLUTION import ReferenceFileLoader, BOMProcessor, Consolidator
from BOM_CONSOLIDATION_MULTI_FORMAT import PnLProcessor, CustomerLocationExtractor

ITEM_MAPPING = {
    'network rack (dlc)': 'IR9148',
    'network rack (ac)': 'IR9048',
}


class PnLProcessorEnhanced(PnLProcessor):
    """Enhanced PnL processor with complete item extraction"""

    def process(self):
        wb = openpyxl.load_workbook(self.bom_file)
        pnl_sheets = [s for s in wb.sheetnames if 'PnL' in s]
        if not pnl_sheets:
            return []

        ws = wb[pnl_sheets[0]]
        print(f"   📋 Using sheet: '{pnl_sheets[0]}'")

        items = []
        current_section = 'Scale out Networking'

        for row_idx, row in enumerate(ws.iter_rows(min_row=2, values_only=False), 2):
            type_cell = row[0].value if len(row) > 0 else None
            section_cell = row[1].value if len(row) > 1 else None
            model_name_cell = row[2].value if len(row) > 2 else None
            nvidia_pn_cell = row[3].value if len(row) > 3 else None
            description_cell = row[4].value if len(row) > 4 else None
            units_cell = row[5].value if len(row) > 5 else None

            if section_cell and isinstance(section_cell, str):
                if 'Rack Infrastructure' in section_cell or 'Networking Racks' in section_cell:
                    current_section = 'Rack Infrastructure'
                elif any(x in section_cell for x in ['RoCE', 'E-W', 'N-S', 'Fabric', 'OOB']):
                    current_section = 'Scale out Networking'

            has_model = model_name_cell and isinstance(model_name_cell, str)
            has_PN = nvidia_pn_cell and isinstance(nvidia_pn_cell, str)

            if has_model or has_PN:
                qty = 0
                if units_cell:
                    try:
                        qty = int(units_cell) if isinstance(units_cell, (int, float)) else 0
                    except (ValueError, TypeError):
                        qty = 0

                model_name_str = str(model_name_cell).strip() if model_name_cell else ''

                item = {
                    'section': current_section,
                    'model_pn': model_name_str or (str(nvidia_pn_cell).strip() if nvidia_pn_cell else 'Unknown'),
                    'nvidia_pn': str(nvidia_pn_cell).strip() if nvidia_pn_cell else '',
                    'dell_pn': '',
                    'description': str(description_cell).strip() if description_cell else '',
                    'quantity': qty
                }

                if qty > 0 or 'network rack' in model_name_str.lower():
                    if self.reference_loader and item['nvidia_pn']:
                        ref_match = self.reference_loader.find_item(item['nvidia_pn'])
                        if ref_match:
                            item['dell_pn'] = ref_match.get('dell_pn', '')

                    items.append(item)

        print(f"   ✅ Extracted {len(items)} items")
        return items


class ConsolidatorEnhanced(Consolidator):
    """Enhanced consolidator with item mapping"""

    def add_bom_items(self, items, file_name):
        for item in items:
            model_pn = item.get('model_pn', '')
            qty = item.get('quantity', 0)

            if not model_pn or qty <= 0:
                continue

            mapped_model_pn = model_pn
            model_lower = model_pn.lower()
            for anthropic_item, iren_equivalent in ITEM_MAPPING.items():
                if anthropic_item in model_lower:
                    mapped_model_pn = iren_equivalent
                    break

            key = mapped_model_pn.lower().replace(' ', '').replace('-', '')

            if key not in self.consolidated:
                self.consolidated[key] = {
                    'model_pn': mapped_model_pn,
                    'nvidia_pn': item.get('nvidia_pn', ''),
                    'dell_pn': item.get('dell_pn', ''),
                    'description': item.get('description', ''),
                    'section': item.get('section', 'Unknown'),
                    'category': 'Unknown',
                    'file_quantities': defaultdict(int),
                    'total_quantity': 0
                }

            self.consolidated[key]['file_quantities'][file_name] += qty
            self.consolidated[key]['total_quantity'] += qty

        self.all_files.append(file_name)

    def get_consolidated(self):
        items = [item for item in self.consolidated.values() if item['total_quantity'] > 0]

        for item in items:
            if item['category'] in ['Rack', 'Panel']:
                item['category'] = 'Rack'

        return sorted(items, key=lambda x: x['total_quantity'], reverse=True)


class MergeConsolidationV2:

    def __init__(self, reference_file, bom_files_dir):
        self.reference_file = reference_file
        self.bom_files_dir = Path(bom_files_dir)
        self.reference_loader = None

    def run(self, output_file):
        print("\n" + "="*80)
        print("BOM CONSOLIDATION MERGE V2 - Enhanced with Item Mapping & Categorization")
        print("="*80)

        print("\n📚 Loading reference files...")
        self.reference_loader = ReferenceFileLoader(self.reference_file)

        iren_files = sorted(self.bom_files_dir.glob('BOM - NETWORK - *.xlsx'))
        pnl_files = sorted(self.bom_files_dir.glob('PNL-NETWORK BOM-*.xlsx'))

        print(f"\n🔍 Found {len(iren_files)} IREN L11 BOM files")
        print(f"🔍 Found {len(pnl_files)} Anthropic PnL BOM files")

        print(f"\n📋 Processing IREN L11 BOM files:")
        consolidator_iren = ConsolidatorEnhanced()
        iren_file_locations = {}

        for bom_file in iren_files:
            print(f"\n📄 {bom_file.name}")
            processor = BOMProcessor(bom_file, self.reference_loader)
            items = processor.process()

            if items:
                consolidator_iren.add_bom_items(items, bom_file.name)
                customer, location = self._extract_iren_location(bom_file.name)
                iren_file_locations[bom_file.name] = {'customer': customer, 'location': location}
                print(f"   ✅ Extracted {len(items)} items")

        print(f"\n📋 Processing Anthropic PnL BOM files:")
        consolidator_pnl = ConsolidatorEnhanced()
        pnl_file_locations = {}

        for bom_file in pnl_files:
            print(f"\n📄 {bom_file.name}")
            processor = PnLProcessorEnhanced(bom_file, self.reference_loader)
            items = processor.process()

            if items:
                consolidator_pnl.add_bom_items(items, bom_file.name)
                customer, location = CustomerLocationExtractor.extract_from_filename(bom_file.name)
                pnl_file_locations[bom_file.name] = {'customer': customer, 'location': location}

        print(f"\n🔄 Merging IREN and Anthropic data with item mapping...")
        merged_consolidator = self._merge_consolidators(consolidator_iren, consolidator_pnl)

        print(f"\n💾 Generating Excel output...")
        all_files = consolidator_iren.all_files + consolidator_pnl.all_files
        all_file_locations = {**iren_file_locations, **pnl_file_locations}

        generator = ExcelGeneratorMergedV2(merged_consolidator, all_file_locations)
        output_path = generator.generate(output_file)

        self._print_summary(merged_consolidator, all_files, output_path)

        return output_path

    @staticmethod
    def _extract_iren_location(filename: str):
        location_map = {
            'Mackenzie': 'Mackenzie, BC',
            'PS': 'Prince George, BC',
            'Sweetwater': 'Sweetwater, WY',
            'B200': 'Childress, TX',
            'B300': 'Childress, TX',
            'CHLD_HORIZON': 'Childress, TX',
        }

        for key, location in location_map.items():
            if key.lower() in filename.lower():
                return 'IREN', location
        return 'IREN', ''

    def _merge_consolidators(self, iren_consolidator, pnl_consolidator):
        merged = ConsolidatorEnhanced()
        merged.all_files = iren_consolidator.all_files + pnl_consolidator.all_files

        for key, item in iren_consolidator.consolidated.items():
            item_copy = copy.deepcopy(item)
            for pnl_file in pnl_consolidator.all_files:
                if pnl_file not in item_copy['file_quantities']:
                    item_copy['file_quantities'][pnl_file] = 0
            merged.consolidated[key] = item_copy

        for key, item in pnl_consolidator.consolidated.items():
            if key not in merged.consolidated:
                item_copy = copy.deepcopy(item)
                for iren_file in iren_consolidator.all_files:
                    if iren_file not in item_copy['file_quantities']:
                        item_copy['file_quantities'][iren_file] = 0
                merged.consolidated[key] = item_copy
            else:
                for file_name, qty in item['file_quantities'].items():
                    if file_name not in merged.consolidated[key]['file_quantities']:
                        merged.consolidated[key]['file_quantities'][file_name] = 0
                    merged.consolidated[key]['file_quantities'][file_name] += qty
                merged.consolidated[key]['total_quantity'] += item['total_quantity']

        return merged

    def _print_summary(self, consolidator, all_files, output_path):
        items = consolidator.get_consolidated()
        total_qty = sum(item['total_quantity'] for item in items)

        categories = defaultdict(int)
        for item in items:
            categories[item['category']] += 1

        print("\n" + "="*80)
        print("MERGE CONSOLIDATION SUMMARY V2")
        print("="*80)
        print(f"Total files: {len(all_files)}")
        print(f"Total unique items: {len(items)}")
        print(f"Total quantity: {total_qty:,}")

        print(f"\nBy category:")
        for cat in sorted(categories.keys()):
            print(f"  {cat:20} | Items: {categories[cat]:3}")

        print("\n" + "="*80)
        print(f"📊 OUTPUT FILE:")
        print(f"📍 {output_path}")
        print("="*80)
        print("✅ Merge consolidation V2 complete!")


class ExcelGeneratorMergedV2:

    def __init__(self, consolidator, file_locations):
        self.consolidator = consolidator
        self.file_locations = file_locations

    def generate(self, output_file):
        wb = openpyxl.Workbook()
        wb.remove(wb.active)

        file_names = self.consolidator.all_files
        items = self.consolidator.get_consolidated()

        self._create_summary_per_sections(wb, items, file_names)
        self._create_summary_total(wb, items, file_names)
        self._create_summary_comparison(wb, items, file_names)

        wb.save(output_file)
        print(f"   ✅ Excel file created: {output_file}")
        return output_file

    def _create_summary_per_sections(self, wb, items, file_names):
        ws = wb.create_sheet('Summary per sections')

        headers = ['Section', 'Model/PN', 'NVIDIA Generic Part number', 'Dell PN', 'Description', 'Category']
        headers.extend(file_names)
        headers.append('Total per Section')

        for col_idx, header in enumerate(headers, 1):
            ws.cell(row=1, column=col_idx, value=header)

        ws['A2'] = 'Customer'
        ws['A3'] = 'Location'
        ws['A4'] = 'Delivery Date'

        for col_offset, file_name in enumerate(file_names):
            col_idx = 7 + col_offset
            customer = self.file_locations.get(file_name, {}).get('customer', '')
            location = self.file_locations.get(file_name, {}).get('location', '')

            ws.cell(row=2, column=col_idx, value=customer)
            ws.cell(row=3, column=col_idx, value=location)
            ws.cell(row=4, column=col_idx, value='')

        row_num = 5
        for item in items:
            row_data = [
                item['section'],
                item['model_pn'],
                item['nvidia_pn'] or '',
                item['dell_pn'] or '',
                item['description'] or '',
                item['category']
            ]

            for file_name in file_names:
                qty = item['file_quantities'].get(file_name, 0)
                row_data.append(qty)

            row_data.append(item['total_quantity'])

            for col_idx, value in enumerate(row_data, 1):
                ws.cell(row=row_num, column=col_idx, value=value)

            row_num += 1

    def _create_summary_total(self, wb, items, file_names):
        ws = wb.create_sheet('Summary Total')

        headers = ['Model/PN', 'Description', 'NVIDIA Generic Part number', 'Dell PN', 'Category']
        headers.extend(file_names)
        headers.append('Total Quantity')

        for col_idx, header in enumerate(headers, 1):
            ws.cell(row=1, column=col_idx, value=header)

        ws['A2'] = 'Customer'
        ws['A3'] = 'Location'
        ws['A4'] = 'Delivery Date'

        for col_offset, file_name in enumerate(file_names):
            col_idx = 6 + col_offset
            customer = self.file_locations.get(file_name, {}).get('customer', '')
            location = self.file_locations.get(file_name, {}).get('location', '')

            ws.cell(row=2, column=col_idx, value=customer)
            ws.cell(row=3, column=col_idx, value=location)
            ws.cell(row=4, column=col_idx, value='')

        row_num = 5
        for item in items:
            row_data = [
                item['model_pn'],
                item['description'] or '',
                item['nvidia_pn'] or '',
                item['dell_pn'] or '',
                item['category']
            ]

            for file_name in file_names:
                qty = item['file_quantities'].get(file_name, 0)
                row_data.append(qty)

            row_data.append(item['total_quantity'])

            for col_idx, value in enumerate(row_data, 1):
                ws.cell(row=row_num, column=col_idx, value=value)

            row_num += 1

    def _create_summary_comparison(self, wb, items, file_names):
        ws = wb.create_sheet('Summary total comparison')

        headers = ['Model/PN', 'NVIDIA Generic Part number', 'Dell PN', 'Description', 'Category']
        headers.extend(file_names)
        headers.extend(['Total from File Sections', 'Total from Summary Total Tab', 'Discrepancy', 'Status'])

        for col_idx, header in enumerate(headers, 1):
            ws.cell(row=1, column=col_idx, value=header)

        ws['A2'] = 'Customer'
        ws['A3'] = 'Location'
        ws['A4'] = 'Delivery Date'

        for col_offset, file_name in enumerate(file_names):
            col_idx = 6 + col_offset
            customer = self.file_locations.get(file_name, {}).get('customer', '')
            location = self.file_locations.get(file_name, {}).get('location', '')

            ws.cell(row=2, column=col_idx, value=customer)
            ws.cell(row=3, column=col_idx, value=location)
            ws.cell(row=4, column=col_idx, value='')

        row_num = 5
        for item in items:
            row_data = [
                item['model_pn'],
                item['nvidia_pn'] or '',
                item['dell_pn'] or '',
                item['description'] or '',
                item['category']
            ]

            total_from_sections = 0
            for file_name in file_names:
                qty = item['file_quantities'].get(file_name, 0)
                row_data.append(qty)
                total_from_sections += qty

            total_from_summary = item['total_quantity']
            discrepancy = total_from_summary - total_from_sections
            status = 'MATCH' if discrepancy == 0 else 'MISMATCH'

            row_data.extend([total_from_sections, total_from_summary, discrepancy, status])

            for col_idx, value in enumerate(row_data, 1):
                ws.cell(row=row_num, column=col_idx, value=value)

            row_num += 1


if __name__ == "__main__":
    import os

    current_dir = Path.cwd()

    REFERENCE_FILE = str(current_dir / "Dell Networking components list details WO Pricing.xlsx")
    BOM_FILES_DIR = str(current_dir)
    OUTPUT_FILE = str(current_dir / "BOM_CONSOLIDATED_FINAL.xlsx")

    if not os.path.exists(REFERENCE_FILE):
        print(f"❌ ERROR: Reference file not found")
        exit(1)

    pipeline = MergeConsolidationV2(REFERENCE_FILE, BOM_FILES_DIR)
    pipeline.run(OUTPUT_FILE)
