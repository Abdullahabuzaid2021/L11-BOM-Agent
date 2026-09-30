"""
BOM Consolidation Script - Multi-format (IREN L11 + Anthropic PnL)
Consolidates both IREN L11 BOM files and Anthropic PnL BOM files
"""

from pathlib import Path
import openpyxl
from openpyxl.utils import get_column_letter
from collections import defaultdict
import re


class PnLProcessor:
    """Process Anthropic PnL format BOM files"""

    def __init__(self, bom_file, reference_loader):
        self.bom_file = bom_file
        self.reference_loader = reference_loader
        self.items = []

    def process(self):
        """Extract items from PnL sheet"""
        wb = openpyxl.load_workbook(self.bom_file)

        # Find PnL sheet
        pnl_sheets = [s for s in wb.sheetnames if 'PnL' in s]
        if not pnl_sheets:
            print(f"   ⚠️  No PnL sheet found in {self.bom_file.name}")
            return []

        ws = wb[pnl_sheets[0]]
        print(f"   📋 Using sheet: '{pnl_sheets[0]}'")

        current_section = 'Scale out Networking'
        items = []

        # Parse rows starting from row 2
        for row_idx, row in enumerate(ws.iter_rows(min_row=2, values_only=False), 2):
            # Get cell values
            type_cell = row[0].value if len(row) > 0 else None
            networking_cell = row[1].value if len(row) > 1 else None
            nvidia_pn_cell = row[2].value if len(row) > 2 else None
            dell_pn_cell = row[3].value if len(row) > 3 else None
            description_cell = row[4].value if len(row) > 4 else None
            units_cell = row[5].value if len(row) > 5 else None

            # Update section if indicated
            if type_cell and not nvidia_pn_cell and networking_cell and isinstance(networking_cell, str):
                if any(x in networking_cell for x in ['RoCE', 'E-W', 'N-S', 'Fabric']):
                    current_section = 'Scale out Networking'

            # Skip header rows and empty rows
            if not nvidia_pn_cell or not isinstance(nvidia_pn_cell, str):
                continue

            # Skip rows without quantity
            if not units_cell or (isinstance(units_cell, (int, float)) and units_cell == 0):
                continue

            try:
                qty = int(units_cell) if isinstance(units_cell, (int, float)) else 0
                if qty <= 0:
                    continue
            except (ValueError, TypeError):
                continue

            # Extract item data
            item = {
                'section': current_section,
                'model_pn': str(nvidia_pn_cell).strip(),
                'nvidia_pn': str(nvidia_pn_cell).strip(),
                'dell_pn': str(dell_pn_cell).strip() if dell_pn_cell else '',
                'description': str(description_cell).strip() if description_cell else '',
                'quantity': qty
            }

            # Match to reference for additional details
            if self.reference_loader:
                ref_match = self.reference_loader.find_item(item['model_pn'])
                if ref_match:
                    item['nvidia_pn'] = ref_match.get('nvidia_pn', item['nvidia_pn'])
                    item['dell_pn'] = ref_match.get('dell_pn', item['dell_pn'])
                    item['reference_type'] = ref_match.get('type', '')

            items.append(item)

        print(f"   ✅ Extracted {len(items)} items")
        return items


class CustomerLocationExtractor:
    """Extract customer and location from various BOM file formats"""

    # IREN location mapping
    IREN_LOCATION_MAP = {
        'Mackenzie': 'Mackenzie, BC',
        'PS': 'Prince George, BC',
        'Prince George': 'Prince George, BC',
        'Sweetwater': 'Sweetwater, WY',
        'B200': 'Childress, TX',
        'B300': 'Childress, TX',
        'CHLD_HORIZON': 'Childress, TX',
        'HORIZON': 'Childress, TX',
    }

    # Anthropic location mapping
    ANTHROPIC_LOCATION_MAP = {
        'Australia': 'Sydney, AU',
        'Canada': 'Toronto, CA',
        'US': 'New York, US',
    }

    @staticmethod
    def extract_from_filename(filename: str):
        """Extract customer and location from BOM filename"""
        filename_lower = filename.lower()

        # Check for IREN format
        if 'iren' in filename_lower:
            customer = 'IREN'
            location = CustomerLocationExtractor._extract_iren_location(filename_lower)
            return customer, location

        # Check for Anthropic format
        if 'anthropic' in filename_lower:
            customer = 'Anthropic'
            location = CustomerLocationExtractor._extract_anthropic_location(filename_lower)
            return customer, location

        return '', ''

    @staticmethod
    def _extract_iren_location(filename_lower: str) -> str:
        """Extract location from IREN BOM filename"""
        for key, location in CustomerLocationExtractor.IREN_LOCATION_MAP.items():
            if key.lower() in filename_lower:
                return location
        return ''

    @staticmethod
    def _extract_anthropic_location(filename_lower: str) -> str:
        """Extract location from Anthropic PnL filename"""
        for key, location in CustomerLocationExtractor.ANTHROPIC_LOCATION_MAP.items():
            if key.lower() in filename_lower:
                return location
        return ''


class ConsolidatorMultiFormat:
    """Consolidate items from both IREN and Anthropic formats"""

    def __init__(self):
        self.consolidated = {}
        self.all_files = []
        self.file_locations = {}

    def add_items(self, items, file_name, customer, location):
        """Add items from a BOM file"""
        self.all_files.append(file_name)
        self.file_locations[file_name] = {'customer': customer, 'location': location}

        for item in items:
            model_pn = item.get('model_pn')
            qty = item.get('quantity', 0)

            # Skip items without model_pn
            if not model_pn:
                continue

            # Create key for consolidation
            key = str(model_pn).lower().replace(' ', '')

            if key not in self.consolidated:
                self.consolidated[key] = {
                    'model_pn': model_pn,
                    'nvidia_pn': item.get('nvidia_pn', ''),
                    'dell_pn': item.get('dell_pn', ''),
                    'description': item.get('description', ''),
                    'section': item.get('section', 'Unknown'),
                    'category': 'Scale out Networking',  # Default for PnL
                    'file_quantities': defaultdict(int),
                    'total_quantity': 0
                }

            self.consolidated[key]['file_quantities'][file_name] += qty
            self.consolidated[key]['total_quantity'] += qty

    def get_consolidated(self):
        """Get consolidated items, excluding zero-quantity items"""
        items = [item for item in self.consolidated.values() if item['total_quantity'] > 0]
        return sorted(items, key=lambda x: x['total_quantity'], reverse=True)


class ExcelGeneratorMultiFormat:
    """Generate consolidated Excel output with both IREN and Anthropic data"""

    def __init__(self, consolidator_iren, consolidator_pnl, reference_file):
        self.consolidator_iren = consolidator_iren
        self.consolidator_pnl = consolidator_pnl
        self.reference_file = reference_file

    def generate(self, output_file):
        """Generate consolidated Excel workbook"""
        wb = openpyxl.Workbook()
        wb.remove(wb.active)  # Remove default sheet

        # Get all files and consolidate
        all_files_iren = self.consolidator_iren.all_files
        all_files_pnl = self.consolidator_pnl.all_files
        all_files = all_files_iren + all_files_pnl

        # Merge items from both consolidators
        merged_items = {}

        for item in self.consolidator_iren.get_consolidated():
            key = item['model_pn'].lower().replace(' ', '')
            merged_items[key] = item

        for item in self.consolidator_pnl.get_consolidated():
            key = item['model_pn'].lower().replace(' ', '')
            if key not in merged_items:
                merged_items[key] = item
            else:
                # Merge quantities
                for file_name, qty in item['file_quantities'].items():
                    merged_items[key]['file_quantities'][file_name] += qty
                merged_items[key]['total_quantity'] += item['total_quantity']

        items = sorted(merged_items.values(), key=lambda x: x['total_quantity'], reverse=True)

        # Create sheets
        self._create_summary_combined(wb, items, all_files)

        # Save
        wb.save(output_file)
        print(f"   ✅ Excel file created: {output_file}")

        return output_file

    def _create_summary_combined(self, wb, items, file_names):
        """Create summary sheet with both IREN and Anthropic data"""
        ws = wb.create_sheet('Summary Combined')

        # Row 1: Headers
        headers = ['Model/PN', 'NVIDIA Generic Part number', 'Dell PN', 'Description', 'Section', 'Category']
        headers.extend(file_names)
        headers.append('Total Quantity')

        for col_idx, header in enumerate(headers, 1):
            ws.cell(row=1, column=col_idx, value=header)

        # Row 2-4: Metadata
        ws['A2'] = 'Customer'
        ws['A3'] = 'Location'
        ws['A4'] = 'Delivery Date'

        file_locs_iren = self.consolidator_iren.file_locations
        file_locs_pnl = self.consolidator_pnl.file_locations

        for col_offset, file_name in enumerate(file_names):
            col_idx = 7 + col_offset  # Start after the 6 main columns

            if file_name in file_locs_iren:
                customer = file_locs_iren[file_name].get('customer', '')
                location = file_locs_iren[file_name].get('location', '')
            elif file_name in file_locs_pnl:
                customer = file_locs_pnl[file_name].get('customer', '')
                location = file_locs_pnl[file_name].get('location', '')
            else:
                customer = ''
                location = ''

            ws.cell(row=2, column=col_idx, value=customer)
            ws.cell(row=3, column=col_idx, value=location)
            ws.cell(row=4, column=col_idx, value='')

        # Row 5+: Data
        row_num = 5
        for item in items:
            row_data = [
                item['model_pn'],
                item['nvidia_pn'] or '',
                item['dell_pn'] or '',
                item['description'] or '',
                item['section'],
                item['category']
            ]

            for file_name in file_names:
                qty = item['file_quantities'].get(file_name, 0)
                row_data.append(qty)

            row_data.append(item['total_quantity'])

            for col_idx, value in enumerate(row_data, 1):
                ws.cell(row=row_num, column=col_idx, value=value)

            row_num += 1


class MultiFormatPipeline:
    """Multi-format BOM consolidation pipeline"""

    def __init__(self, reference_file, bom_files_dir):
        self.reference_file = reference_file
        self.bom_files_dir = Path(bom_files_dir)
        self.reference_loader = None

    def run(self, output_file):
        """Run the complete multi-format pipeline"""
        print("\n" + "="*80)
        print("MULTI-FORMAT BOM CONSOLIDATION - IREN L11 + ANTHROPIC PnL")
        print("="*80)

        # Find IREN and Anthropic BOM files
        iren_files = sorted(self.bom_files_dir.glob('BOM - NETWORK - *.xlsx'))
        pnl_files = sorted(self.bom_files_dir.glob('PNL-NETWORK BOM-*.xlsx'))

        print(f"\n🔍 Found {len(iren_files)} IREN L11 BOM files")
        print(f"🔍 Found {len(pnl_files)} Anthropic PnL BOM files")

        # Initialize consolidators
        consolidator_iren = ConsolidatorMultiFormat()
        consolidator_pnl = ConsolidatorMultiFormat()

        # Process IREN files
        if iren_files:
            print(f"\n📋 Processing IREN L11 BOM files:")
            from BOM_CONSOLIDATION_FINAL_SOLUTION import ReferenceFileLoader, BOMProcessor

            self.reference_loader = ReferenceFileLoader(self.reference_file)

            for bom_file in iren_files:
                print(f"\n📄 Processing: {bom_file.name}")
                processor = BOMProcessor(bom_file, self.reference_loader)
                items = processor.process()

                if items:
                    customer, location = CustomerLocationExtractor.extract_from_filename(bom_file.name)
                    consolidator_iren.add_items(items, bom_file.name, customer, location)
                    print(f"   ✅ Extracted {len(items)} items | Customer: {customer} | Location: {location}")

        # Process Anthropic PnL files
        if pnl_files:
            print(f"\n📋 Processing Anthropic PnL BOM files:")
            self.reference_loader = self.reference_loader or ReferenceFileLoader(self.reference_file)

            for bom_file in pnl_files:
                print(f"\n📄 Processing: {bom_file.name}")
                processor = PnLProcessor(bom_file, self.reference_loader)
                items = processor.process()

                if items:
                    customer, location = CustomerLocationExtractor.extract_from_filename(bom_file.name)
                    consolidator_pnl.add_items(items, bom_file.name, customer, location)
                    print(f"   ✅ Extracted {len(items)} items | Customer: {customer} | Location: {location}")

        # Generate output
        print(f"\n💾 Generating Excel output...")
        generator = ExcelGeneratorMultiFormat(consolidator_iren, consolidator_pnl, self.reference_file)
        output_path = generator.generate(output_file)

        # Print summary
        self._print_summary(consolidator_iren, consolidator_pnl, output_file, output_path)

        return output_path

    def _print_summary(self, consolidator_iren, consolidator_pnl, output_file, output_path):
        """Print consolidation summary"""
        items_iren = consolidator_iren.get_consolidated()
        items_pnl = consolidator_pnl.get_consolidated()

        total_qty_iren = sum(item['total_quantity'] for item in items_iren)
        total_qty_pnl = sum(item['total_quantity'] for item in items_pnl)

        print("\n" + "="*80)
        print("CONSOLIDATION SUMMARY")
        print("="*80)
        print(f"\nIREN L11 BOM:")
        print(f"  Unique items: {len(items_iren)}")
        print(f"  Total quantity: {total_qty_iren:,}")
        print(f"  Files processed: {len(consolidator_iren.all_files)}")

        print(f"\nAnthropicPnL BOM:")
        print(f"  Unique items: {len(items_pnl)}")
        print(f"  Total quantity: {total_qty_pnl:,}")
        print(f"  Files processed: {len(consolidator_pnl.all_files)}")

        print(f"\nCombined:")
        print(f"  Total unique items: {len(items_iren) + len(items_pnl)}")
        print(f"  Total quantity: {total_qty_iren + total_qty_pnl:,}")

        print("\n" + "="*80)
        print(f"📊 OUTPUT FILE:")
        print(f"📍 {output_path}")
        print("="*80)
        print("✅ Multi-format consolidation complete!")


# MAIN EXECUTION
if __name__ == "__main__":
    import os

    current_dir = Path.cwd()

    REFERENCE_FILE = str(current_dir / "Dell Networking components list details WO Pricing.xlsx")
    BOM_FILES_DIR = str(current_dir)
    OUTPUT_FILE = str(current_dir / "BOM_CONSOLIDATED_MULTI_FORMAT.xlsx")

    print(f"\n📂 Current directory: {current_dir}")
    print(f"📄 Reference file: {REFERENCE_FILE}")
    print(f"📁 BOM files directory: {BOM_FILES_DIR}")
    print(f"📊 Output file: {OUTPUT_FILE}")

    if not os.path.exists(REFERENCE_FILE):
        print(f"\n❌ ERROR: Reference file not found at {REFERENCE_FILE}")
        exit(1)

    pipeline = MultiFormatPipeline(REFERENCE_FILE, BOM_FILES_DIR)
    pipeline.run(OUTPUT_FILE)
