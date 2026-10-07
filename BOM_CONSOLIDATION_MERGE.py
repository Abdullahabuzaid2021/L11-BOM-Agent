"""
BOM Consolidation Merge - Add Anthropic PnL data to existing IREN consolidation
Keeps the same format, categorization, and sheet structure
"""

from pathlib import Path
import openpyxl
from openpyxl.utils import get_column_letter
from collections import defaultdict
import sys
import copy

# Import from existing module
sys.path.insert(0, str(Path.cwd()))
from BOM_CONSOLIDATION_FINAL_SOLUTION import (
    ReferenceFileLoader, BOMProcessor, Consolidator, ExcelGenerator,
    BOMConsolidationPipeline
)
from BOM_CONSOLIDATION_MULTI_FORMAT import (
    PnLProcessor, CustomerLocationExtractor
)

# Item mapping: Anthropic items to IREN equivalents
ITEM_MAPPING = {
    'network rack (dlc)': 'IR9148',
    'network rack (ac)': 'IR9048',
}

# Create a simple location extractor for IREN files
class IrenLocationExtractor:
    LOCATION_MAP = {
        'Mackenzie': 'Mackenzie, BC',
        'PS': 'Prince George, BC',
        'Prince George': 'Prince George, BC',
        'Sweetwater': 'Sweetwater, WY',
        'B200': 'Childress, TX',
        'B300': 'Childress, TX',
        'CHLD_HORIZON': 'Childress, TX',
        'HORIZON': 'Childress, TX',
    }

    @staticmethod
    def extract_from_filename(filename: str):
        filename_lower = filename.lower()
        for key, location in IrenLocationExtractor.LOCATION_MAP.items():
            if key.lower() in filename_lower:
                return 'IREN', location
        return 'IREN', ''


class MergeConsolidation:
    """Merge Anthropic PnL data into existing IREN consolidation"""

    def __init__(self, reference_file, bom_files_dir):
        self.reference_file = reference_file
        self.bom_files_dir = Path(bom_files_dir)
        self.reference_loader = None
        self.consolidator_iren = None
        self.consolidator_pnl = None

    def run(self, output_file):
        """Run the merge process"""
        print("\n" + "="*80)
        print("BOM CONSOLIDATION MERGE - Adding Anthropic PnL to IREN L11")
        print("="*80)

        # Load reference
        print("\n📚 Loading reference files...")
        self.reference_loader = ReferenceFileLoader(self.reference_file)

        # Find IREN files
        iren_files = sorted(self.bom_files_dir.glob('BOM - NETWORK - *.xlsx'))
        pnl_files = sorted(self.bom_files_dir.glob('PNL-NETWORK BOM-*.xlsx'))

        print(f"\n🔍 Found {len(iren_files)} IREN L11 BOM files")
        print(f"🔍 Found {len(pnl_files)} Anthropic PnL BOM files")

        # Process IREN files
        print(f"\n📋 Processing IREN L11 BOM files:")
        self.consolidator_iren = Consolidator()
        iren_file_locations = {}

        for bom_file in iren_files:
            print(f"\n📄 Processing: {bom_file.name}")
            processor = BOMProcessor(bom_file, self.reference_loader)
            items = processor.process()

            if items:
                self.consolidator_iren.add_bom_items(items, bom_file.name)
                customer, location = IrenLocationExtractor.extract_from_filename(bom_file.name)
                iren_file_locations[bom_file.name] = {'customer': customer, 'location': location}
                print(f"   ✅ Extracted {len(items)} items")

        # Process Anthropic PnL files
        print(f"\n📋 Processing Anthropic PnL BOM files:")
        self.consolidator_pnl = Consolidator()
        pnl_file_locations = {}

        for bom_file in pnl_files:
            print(f"\n📄 Processing: {bom_file.name}")
            processor = PnLProcessor(bom_file, self.reference_loader)
            items = processor.process()

            if items:
                self.consolidator_pnl.add_bom_items(items, bom_file.name)
                customer, location = CustomerLocationExtractor.extract_from_filename(bom_file.name)
                pnl_file_locations[bom_file.name] = {'customer': customer, 'location': location}
                print(f"   ✅ Extracted {len(items)} items")

        # Merge consolidators
        print(f"\n🔄 Merging IREN and Anthropic data...")
        merged_consolidator = self._merge_consolidators(
            self.consolidator_iren,
            self.consolidator_pnl,
            iren_file_locations,
            pnl_file_locations
        )

        # Generate output using same format
        print(f"\n💾 Generating Excel output with merged data...")
        all_files = self.consolidator_iren.all_files + self.consolidator_pnl.all_files
        all_file_locations = {**iren_file_locations, **pnl_file_locations}

        generator = ExcelGeneratorMerged(merged_consolidator, all_file_locations)
        output_path = generator.generate(output_file)

        # Print summary
        self._print_summary(merged_consolidator, all_files, output_file, output_path)

        return output_path

    def _merge_consolidators(self, iren_consolidator, pnl_consolidator, iren_locs, pnl_locs):
        """Merge two consolidators with item mapping and category consolidation"""
        merged = Consolidator()
        merged.all_files = iren_consolidator.all_files + pnl_consolidator.all_files

        # Add IREN items and initialize PnL file slots
        for key, item in iren_consolidator.consolidated.items():
            item_copy = copy.deepcopy(item)
            # Initialize slots for PnL files with 0
            for pnl_file in pnl_consolidator.all_files:
                if pnl_file not in item_copy['file_quantities']:
                    item_copy['file_quantities'][pnl_file] = 0
            merged.consolidated[key] = item_copy

        # Add/merge PnL items with mapping
        for key, item in pnl_consolidator.consolidated.items():
            # Check if this item needs to be mapped to an IREN equivalent
            mapped_item_name = item['model_pn']
            model_lower = mapped_item_name.lower()
            for anthropic_item, iren_equivalent in ITEM_MAPPING.items():
                if anthropic_item in model_lower:
                    mapped_item_name = iren_equivalent
                    break

            # Create key for the (potentially mapped) item
            mapped_key = mapped_item_name.lower().replace(' ', '').replace('-', '')

            # Find if this maps to an existing IREN item
            iren_key = None
            for existing_key, existing_item in merged.consolidated.items():
                if existing_item['model_pn'].lower().replace(' ', '').replace('-', '') == mapped_key:
                    iren_key = existing_key
                    break

            if iren_key:
                # Merge with existing IREN item
                for file_name, qty in item['file_quantities'].items():
                    if file_name not in merged.consolidated[iren_key]['file_quantities']:
                        merged.consolidated[iren_key]['file_quantities'][file_name] = 0
                    merged.consolidated[iren_key]['file_quantities'][file_name] += qty
                merged.consolidated[iren_key]['total_quantity'] += item['total_quantity']
            else:
                # New item from Anthropic - initialize IREN file slots
                item_copy = copy.deepcopy(item)
                item_copy['model_pn'] = mapped_item_name  # Use mapped name
                for iren_file in iren_consolidator.all_files:
                    if iren_file not in item_copy['file_quantities']:
                        item_copy['file_quantities'][iren_file] = 0
                merged.consolidated[mapped_key] = item_copy

        # Consolidate categories: Combine Rack + Panel -> Rack
        for item in merged.consolidated.values():
            if item['category'] in ['Rack', 'Panel']:
                item['category'] = 'Rack'

        return merged

    def _print_summary(self, consolidator, all_files, output_file, output_path):
        """Print merge summary"""
        items = consolidator.get_consolidated()

        total_qty = sum(item['total_quantity'] for item in items)

        print("\n" + "="*80)
        print("MERGE CONSOLIDATION SUMMARY")
        print("="*80)
        print(f"Total files: {len(all_files)}")
        print(f"Total unique items: {len(items)}")
        print(f"Total quantity: {total_qty:,}")

        # Category breakdown
        categories = defaultdict(int)
        for item in items:
            categories[item['category']] += 1

        print(f"\nBy category:")
        for cat in sorted(categories.keys()):
            print(f"  {cat:20} | Items: {categories[cat]:3}")

        print("\n" + "="*80)
        print(f"📊 OUTPUT FILE:")
        print(f"📍 {output_path}")
        print("="*80)
        print("✅ Merge consolidation complete!")


class ExcelGeneratorMerged:
    """Generate merged Excel output with IREN + Anthropic data"""

    def __init__(self, consolidator, file_locations):
        self.consolidator = consolidator
        self.file_locations = file_locations

    def generate(self, output_file):
        """Generate merged Excel workbook"""
        wb = openpyxl.Workbook()
        wb.remove(wb.active)

        file_names = self.consolidator.all_files
        items = self.consolidator.get_consolidated()

        # Create same 3 sheets as original
        self._create_summary_per_sections(wb, items, file_names)
        self._create_summary_total(wb, items, file_names)
        self._create_summary_comparison(wb, items, file_names)

        wb.save(output_file)
        print(f"   ✅ Excel file created: {output_file}")
        return output_file

    def _create_summary_per_sections(self, wb, items, file_names):
        """Create Summary per sections sheet"""
        ws = wb.create_sheet('Summary per sections')

        # Headers
        headers = ['Section', 'Model/PN', 'NVIDIA Generic Part number', 'Dell PN', 'Description', 'Category']
        headers.extend(file_names)
        headers.append('Total per Section')

        for col_idx, header in enumerate(headers, 1):
            ws.cell(row=1, column=col_idx, value=header)

        # Metadata rows
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

        # Data rows
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
        """Create Summary Total sheet"""
        ws = wb.create_sheet('Summary Total')

        # Headers
        headers = ['Model/PN', 'Description', 'NVIDIA Generic Part number', 'Dell PN', 'Category']
        headers.extend(file_names)
        headers.append('Total Quantity')

        for col_idx, header in enumerate(headers, 1):
            ws.cell(row=1, column=col_idx, value=header)

        # Metadata rows
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

        # Data rows
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
        """Create Summary total comparison sheet"""
        ws = wb.create_sheet('Summary total comparison')

        # Headers
        headers = ['Model/PN', 'NVIDIA Generic Part number', 'Dell PN', 'Description', 'Category']
        headers.extend(file_names)
        headers.extend(['Total from File Sections', 'Total from Summary Total Tab', 'Discrepancy', 'Status'])

        for col_idx, header in enumerate(headers, 1):
            ws.cell(row=1, column=col_idx, value=header)

        # Metadata rows
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

        # Data rows
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


# MAIN EXECUTION
if __name__ == "__main__":
    import os

    current_dir = Path.cwd()

    REFERENCE_FILE = str(current_dir / "Dell Networking components list details WO Pricing.xlsx")
    BOM_FILES_DIR = str(current_dir)
    OUTPUT_FILE = str(current_dir / "BOM_CONSOLIDATED_FINAL.xlsx")

    print(f"\n📂 Current directory: {current_dir}")
    print(f"📄 Reference file: {REFERENCE_FILE}")
    print(f"📁 BOM files directory: {BOM_FILES_DIR}")
    print(f"📊 Output file: {OUTPUT_FILE}")

    if not os.path.exists(REFERENCE_FILE):
        print(f"\n❌ ERROR: Reference file not found at {REFERENCE_FILE}")
        exit(1)

    pipeline = MergeConsolidation(REFERENCE_FILE, BOM_FILES_DIR)
    pipeline.run(OUTPUT_FILE)
