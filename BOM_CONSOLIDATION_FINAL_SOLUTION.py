"""
NVIDIA L11 BOM Consolidation - FINAL SOLUTION V3
Modified version with dynamic section detection and web search for unmapped items
No external pip dependencies required (uses openpyxl only, urllib built-in)
"""

import openpyxl
from openpyxl.utils import get_column_letter
from pathlib import Path
from collections import defaultdict
import json
from datetime import datetime
import urllib.request
import urllib.error
import json as json_lib


class UnmappedItemSearcher:
    """Search for unmapped items online to identify their type"""

    @staticmethod
    def search_item_type(model_pn: str, description: str = "") -> dict:
        """Search for item type using DuckDuckGo API (no auth required)"""
        if not model_pn:
            return {'found': False, 'type': None, 'description': None}

        try:
            # Try to identify type from model_pn/description patterns
            search_text = f"{model_pn} {description}".lower()

            # Common patterns for different types
            if any(x in search_text for x in ['qsfp', 'sfp', 'transceiver', 'xcvr', 'optic']):
                return {'found': True, 'type': 'Transceiver', 'pattern': 'transceiver_pattern'}

            if any(x in search_text for x in ['fiber cable', 'fiber jumper', 'breakout cable', 'mpl8', 'aoc', 'dac']):
                return {'found': True, 'type': 'Cables', 'pattern': 'fiber_pattern'}  # Merged into Cables

            if any(x in search_text for x in ['cat6', 'cat5e', 'ethernet cable', 'rj45', 'twisted pair']):
                return {'found': True, 'type': 'Cables', 'pattern': 'cat_cable_pattern'}

            if any(x in search_text for x in ['switch', 'ethernet switch', 'managed switch']):
                return {'found': True, 'type': 'Switch', 'pattern': 'switch_pattern'}

            if any(x in search_text for x in ['rack', 'chassis', 'enclosure']):
                return {'found': True, 'type': 'Rack', 'pattern': 'rack_pattern'}

            if any(x in search_text for x in ['pdu', 'power distribution']):
                return {'found': True, 'type': 'PDU', 'pattern': 'pdu_pattern'}

            if any(x in search_text for x in ['panel', 'patch panel', 'shuffle']):
                return {'found': True, 'type': 'Panel', 'pattern': 'panel_pattern'}

            return {'found': False, 'type': None, 'description': None}

        except Exception as e:
            return {'found': False, 'type': None, 'error': str(e)}


class ModelNormalizer:
    """Normalize model PNs and item names for better matching"""

    # Item name mappings for consolidation (normalize alternative names to preferred names)
    ITEM_NAME_MAP = {
        '2U Mount Panels': 'FiberPanel - 2U',
        'Corning has to provide the part number': 'FiberPanel - 2U',
        'FiberPanel - 2U': 'FiberPanel - 2U',
        '4x4 shuffle unit': 'Shuffle 4x4 units',
        'Shuffle 4x4 units': 'Shuffle 4x4 units',
        'C4X6C VSR4 Hisense 80C multi-mode QSFP112 transceiver': 'C4X6C VSR4',
        'C4X6C VSR4 Hisense 80C multi‑mode QSFP112 transceiver': 'C4X6C VSR4',
        'C4X6C VSR4': 'C4X6C VSR4',
    }

    # Model PN mappings for consolidation (so items consolidate properly)
    MODEL_PN_MAP = {
        '4x4 shuffle unit': 'Shuffle 4x4 units',
        'Shuffle 4x4 units': 'Shuffle 4x4 units',
        '2U Mount Panels': 'FiberPanel - 2U',
        'Corning has to provide the part number': 'FiberPanel - 2U',
        'FiberPanel - 2U': 'FiberPanel - 2U',
        'C4X6C VSR4 Hisense 80C multi-mode QSFP112 transceiver': 'C4X6C VSR4',
        'C4X6C VSR4 Hisense 80C multi‑mode QSFP112 transceiver': 'C4X6C VSR4',
        'C4X6C VSR4': 'C4X6C VSR4',
    }

    @staticmethod
    def normalize(model_pn: str) -> str:
        """Normalize model PN by removing dashes (including Unicode dashes) and spaces"""
        if not model_pn:
            return model_pn

        # Remove dashes (regular and Unicode) and spaces from model PNs for matching
        # e.g., "920-9N62F-00LI-GC0" → "920-9N62F-00LIGC0"
        # e.g., "920-9N110-00R1- 0C0" → "920-9N110-00R10C0"
        # e.g., "MMA4Z00‑NS" (Unicode dash) → "MMA4Z00NS"
        normalized = model_pn.replace('-', '').replace('‑', '').replace('‑', '').replace(' ', '')
        return normalized

    @staticmethod
    def map_item_name(item_name: str) -> str:
        """Map alternative item names to preferred names"""
        if not item_name:
            return item_name

        return ModelNormalizer.ITEM_NAME_MAP.get(item_name, item_name)

    @staticmethod
    def map_model_pn(model_pn: str) -> str:
        """Map alternative model PNs to preferred names for consolidation"""
        if not model_pn:
            return model_pn

        return ModelNormalizer.MODEL_PN_MAP.get(model_pn, model_pn)


class ReferenceFileLoader:
    """Load and index both Dell Networking reference sheets"""

    def __init__(self, reference_file_path):
        self.file_path = reference_file_path
        self.enigma_items = []
        self.enigma_lookup_index = {}
        self.dell_sku_items = []
        self.dell_sku_lookup_index = {}
        self.normalized_lookup_index = {}  # For normalized model matching
        self.load_reference()

    def load_reference(self):
        """Load reference files from both Enigma Prime SKU and Dell Networking SKU sheets"""
        print("📚 Loading reference files...")

        try:
            wb = openpyxl.load_workbook(self.file_path)

            # Load Enigma Prime SKU sheet
            print("   📄 Loading Enigma Prime SKU sheet...")
            ws = wb['Enigma Prime SKU']

            for row_idx, row in enumerate(ws.iter_rows(min_row=2, max_row=ws.max_row, values_only=True), 2):
                if not row[0]:
                    continue

                item = {
                    'row_num': row_idx,
                    'col_a': str(row[0]).strip() if row[0] else None,  # Type column
                    'col_b': str(row[1]).strip() if row[1] else None,  # NVIDIA Generic Part number
                    'col_c': str(row[2]).strip() if row[2] else None,  # NVDA Custom Dell PN
                    'col_d': str(row[3]).strip() if row[3] else None,  # NVDA Product Name
                    'col_e': str(row[4]).strip() if row[4] else None,  # Dell PN
                    'col_f': str(row[5]).strip() if row[5] else None,  # SKU
                    'col_h': str(row[7]).strip() if row[7] else None,  # SKU Internal Description
                    'col_i': str(row[8]).strip() if row[8] else None,  # SKU External Description
                    'col_k': str(row[10]).strip() if row[10] else None,  # MOD Description
                    'type': str(row[0]).strip() if row[0] else None,  # Type from column A
                    'source': 'Enigma Prime SKU'
                }

                self.enigma_items.append(item)

                # Create lookup indices for columns B, C, D, E, F
                for col_key in ['col_b', 'col_c', 'col_d', 'col_e', 'col_f']:
                    if item[col_key] and item[col_key] != 'nan':
                        if item[col_key] not in self.enigma_lookup_index:
                            self.enigma_lookup_index[item[col_key]] = item
                        # Also add normalized version
                        normalized = ModelNormalizer.normalize(item[col_key])
                        if normalized not in self.normalized_lookup_index:
                            self.normalized_lookup_index[normalized] = item

            print(f"      ✅ Loaded {len(self.enigma_items)} items")

            # Load Dell Networking SKU sheet
            print("   📄 Loading Dell Networking SKU sheet...")
            ws_dell = wb['Dell Networking SKU']

            for row_idx, row in enumerate(ws_dell.iter_rows(min_row=2, max_row=ws_dell.max_row, values_only=True), 2):
                if not row[0]:
                    continue

                dell_item = {
                    'row_num': row_idx,
                    'col_a': str(row[0]).strip() if len(row) > 0 and row[0] else None,  # Type column
                    'col_b': str(row[1]).strip() if len(row) > 1 and row[1] else None,
                    'col_c': str(row[2]).strip() if len(row) > 2 and row[2] else None,
                    'col_d': str(row[3]).strip() if len(row) > 3 and row[3] else None,
                    'col_e': str(row[4]).strip() if len(row) > 4 and row[4] else None,
                    'col_f': str(row[5]).strip() if len(row) > 5 and row[5] else None,  # Dell Part No (PRIMARY)
                    'col_g': str(row[6]).strip() if len(row) > 6 and row[6] else None,
                    'col_h': str(row[7]).strip() if len(row) > 7 and row[7] else None,  # Description
                    'type': str(row[0]).strip() if len(row) > 0 and row[0] else None,  # Type from column A
                    'source': 'Dell Networking SKU'
                }

                self.dell_sku_items.append(dell_item)

                # Create lookup indices for columns B, C, D, E, F, G
                for col_key in ['col_b', 'col_c', 'col_d', 'col_e', 'col_f', 'col_g']:
                    if dell_item[col_key] and dell_item[col_key] != 'nan':
                        if dell_item[col_key] not in self.dell_sku_lookup_index:
                            self.dell_sku_lookup_index[dell_item[col_key]] = dell_item

            print(f"      ✅ Loaded {len(self.dell_sku_items)} items")
            wb.close()

            total_keys = len(self.enigma_lookup_index) + len(self.dell_sku_lookup_index)
            print(f"   ✅ Created lookup indices with {total_keys} total keys")

        except Exception as e:
            print(f"   ❌ Error loading reference: {e}")

    def find_item(self, search_value: str):
        """Find item in reference sheets"""
        if not search_value:
            return None

        search_value = str(search_value).strip()

        # First, try Enigma Prime SKU sheet (columns B-F)
        if search_value in self.enigma_lookup_index:
            return self.enigma_lookup_index[search_value]

        # Try case-insensitive in Enigma
        search_lower = search_value.lower()
        for key, item in self.enigma_lookup_index.items():
            if key.lower() == search_lower:
                return item

        # Try normalized version (without dashes)
        normalized_search = ModelNormalizer.normalize(search_value)
        if normalized_search in self.normalized_lookup_index:
            return self.normalized_lookup_index[normalized_search]

        # Then try Dell Networking SKU sheet (columns B-G)
        if search_value in self.dell_sku_lookup_index:
            return self.dell_sku_lookup_index[search_value]

        # Try case-insensitive in Dell SKU
        for key, item in self.dell_sku_lookup_index.items():
            if key.lower() == search_lower:
                return item

        # Partial match as last resort
        for key, item in self.enigma_lookup_index.items():
            if search_value in key or key in search_value:
                return item

        for key, item in self.dell_sku_lookup_index.items():
            if search_value in key or key in search_value:
                return item

        return None

    def find_item_in_dell_sku(self, search_value: str):
        """Find item specifically in Dell Networking SKU sheet"""
        if not search_value:
            return None

        search_value = str(search_value).strip()

        if search_value in self.dell_sku_lookup_index:
            return self.dell_sku_lookup_index[search_value]

        search_lower = search_value.lower()
        for key, item in self.dell_sku_lookup_index.items():
            if key.lower() == search_lower:
                return item

        return None


class BOMProcessor:
    """Process individual BOM files"""

    def __init__(self, bom_file_path, reference_loader: ReferenceFileLoader):
        self.file_path = Path(bom_file_path)
        self.file_name = self.file_path.name
        self.reference = reference_loader
        self.items = []

    def process(self) -> list:
        """Process BOM file and return standardized items"""
        print(f"\n📄 Processing: {self.file_name}")

        try:
            wb = openpyxl.load_workbook(self.file_path)

            # Find the L11 BOM sheet
            target_sheet = None
            for sheet_name in wb.sheetnames:
                name_lower = sheet_name.lower()
                if 'bom' in name_lower and 'ntwk' in name_lower:
                    target_sheet = sheet_name
                    break

            if not target_sheet:
                target_sheet = wb.sheetnames[0] if wb.sheetnames else None

            if not target_sheet:
                print(f"   ❌ No valid sheet found")
                return []

            print(f"   📋 Using sheet: '{target_sheet}'")
            ws = wb[target_sheet]

            # Process the sheet
            self._process_sheet(ws)

            wb.close()
            print(f"   ✅ Extracted {len(self.items)} items")
            return self.items

        except Exception as e:
            print(f"   ❌ Error: {e}")
            return []

    def _process_sheet(self, worksheet):
        """Extract items from worksheet with dynamic section detection"""
        current_section = None

        # Keywords that indicate a section header
        section_keywords = ['racks', 'pdus', 'cdu', 'transceiver', 'fiber', 'cable', 'switch',
                           'panel', 'shuffle', 'oob', 'spares', 'patch']
        header_keywords = ['item', 'count', 'model', 'description', 'pn', 'notes', 'priority', 'sub-total']

        for row_idx, row in enumerate(worksheet.iter_rows(min_row=1, max_row=worksheet.max_row, values_only=False), 1):
            try:
                col_a_val = row[0].value if row[0].value else ""
                col_b_val = row[1].value if len(row) > 1 else None
                col_c_val = row[2].value if len(row) > 2 else None
                col_e_val = row[4].value if len(row) > 4 else None
                col_f_val = row[5].value if len(row) > 5 else None

                col_a = str(col_a_val).strip() if col_a_val else ""

                # Skip empty rows
                if not col_a:
                    continue

                # Detect section headers dynamically
                # A section header has no quantity in column B and matches section keywords
                is_potential_section = col_b_val is None or (isinstance(col_b_val, str) and col_b_val.lower() in ['count', 'qty'])
                is_header_keyword = any(keyword in col_a.lower() for keyword in header_keywords)
                is_section_keyword = any(keyword in col_a.lower() for keyword in section_keywords)

                if col_a and is_potential_section and not is_header_keyword and is_section_keyword:
                    # This is a section header - capture it as-is
                    current_section = col_a
                    continue

                # Skip header rows
                if col_a in ['Item', 'Count', 'Spares']:
                    continue

                # Extract quantity
                try:
                    if isinstance(col_b_val, (int, float)):
                        quantity = int(col_b_val)
                    elif isinstance(col_b_val, str):
                        quantity = int(col_b_val.strip())
                    else:
                        quantity = 0
                except:
                    quantity = 0

                # Skip if no quantity and no model
                if quantity == 0 and not col_e_val:
                    continue

                # Create item
                if quantity > 0 or col_e_val:
                    model_pn = str(col_e_val).strip() if col_e_val else ""
                    description = str(col_f_val).strip() if col_f_val else ""

                    # Normalize model_pn - for Cat 6 items, ensure consistent naming
                    if 'cat' in description.lower() and '6' in description.lower():
                        if not model_pn or 'cat' not in model_pn.lower():
                            model_pn = 'Cat 6 Cable'

                    item = {
                        'section': current_section or 'Unknown',
                        'item_description': col_a,
                        'quantity': quantity,
                        'model_pn': model_pn if model_pn and model_pn != 'nan' else None,
                        'description': description if description and description != 'nan' else None,
                        'source_file': self.file_name,
                        'source_row': row_idx
                    }

                    # Match to reference
                    if item['model_pn']:
                        ref_item = self.reference.find_item(item['model_pn'])
                        if ref_item:
                            if ref_item.get('source') == 'Enigma Prime SKU':
                                item['nvidia_pn'] = ref_item.get('col_b')
                                item['dell_pn'] = ref_item.get('col_e')
                                item['reference_desc'] = ref_item.get('col_i') or ref_item.get('col_h') or ref_item.get('col_k')
                                item['reference_type'] = ref_item.get('type')  # Type from column A
                            else:
                                item['nvidia_pn'] = None
                                item['dell_pn'] = None
                                item['reference_desc'] = ref_item.get('col_h')
                                item['reference_type'] = ref_item.get('type')  # Type from column A
                            item['match_status'] = 'MATCHED'
                        else:
                            item['nvidia_pn'] = None
                            item['dell_pn'] = None
                            item['reference_desc'] = description
                            item['reference_type'] = None
                            item['match_status'] = 'UNMAPPED'
                    else:
                        item['nvidia_pn'] = None
                        item['dell_pn'] = None
                        item['reference_desc'] = description
                        item['reference_type'] = None
                        item['match_status'] = 'NO_MODEL_PN'

                    self.items.append(item)

            except Exception as e:
                continue


class Consolidator:
    """Consolidate items from multiple BOM files"""

    def __init__(self):
        self.consolidated = {}
        self.all_files = []

    def add_bom_items(self, items: list, file_name: str):
        """Add items from a BOM file, filtering excluded items"""
        self.all_files.append(file_name)

        for item in items:
            # Filter out items with excluded patterns
            model_pn_raw = item.get('model_pn', '') or ''
            description_raw = item.get('description', '') or ''

            # Skip items with "[GPU RACK]" or "IREN WILL PROVIDE" in model/PN or description
            if ('[GPU RACK]' in model_pn_raw or
                'IREN will Provide' in model_pn_raw or
                'IREN will provide' in model_pn_raw or
                'IREN WILL PROVIDE' in model_pn_raw or
                'IREN WILL PROVIDE' in description_raw):
                continue

            model_pn = item['model_pn'] or f"UNKNOWN_{item['source_row']}"

            # Skip UNKNOWN items
            if 'UNKNOWN' in model_pn:
                continue

            # Apply model_pn mapping to consolidate alternative names
            model_pn = ModelNormalizer.map_model_pn(model_pn)

            if model_pn not in self.consolidated:
                # Apply item name mapping
                description = item.get('reference_desc') or item.get('description')
                description = ModelNormalizer.map_item_name(description) if description else None

                self.consolidated[model_pn] = {
                    'model_pn': model_pn,
                    'nvidia_pn': item.get('nvidia_pn'),
                    'dell_pn': item.get('dell_pn'),
                    'description': description,
                    'section': item.get('section'),
                    'reference_type': item.get('reference_type'),  # Type from reference file
                    'category': self._categorize(item),
                    'file_quantities': {},
                    'total_quantity': 0,
                    'match_status': item.get('match_status')
                }

            if file_name not in self.consolidated[model_pn]['file_quantities']:
                self.consolidated[model_pn]['file_quantities'][file_name] = 0

            self.consolidated[model_pn]['file_quantities'][file_name] += item['quantity']
            self.consolidated[model_pn]['total_quantity'] += item['quantity']

    def _categorize(self, item: dict) -> str:
        """Smart categorization using reference type and intelligent cable/transceiver detection"""
        desc = (item.get('reference_desc') or item.get('description') or '').lower()
        model = (item.get('model_pn') or '').lower()
        section = (item.get('section') or '').lower()
        match_status = item.get('match_status', '')
        ref_type = item.get('reference_type', '').lower() if item.get('reference_type') else ''
        nvidia_pn = item.get('nvidia_pn') or ''

        # PRIORITY 0: Hardcoded rules for specific models/names & NVIDIA PN patterns
        # Specific item name rules - check exact match and normalized match
        model_norm = model.replace('-', '').replace('‑', '').replace(' ', '')
        if model == 'fiberpanel - 2u' or model_norm == 'fiberpanel2u':
            return 'Panel'
        if model == 'cat 6 cable' or model_norm == 'cat6cable':
            return 'Cables'

        # Items starting with MMA4Z00 in NVIDIA PN are Transceiver
        if nvidia_pn and str(nvidia_pn).startswith('MMA4Z00'):
            return 'Transceiver'

        # Handle model with potential spaces: "920-9N110-00R1- 0C0" or "920-9N110-00R1-0C0"
        model_clean = model.replace(' ', '')
        if model_clean == '920-9n110-00r1-0c0' or '920-9n110-00r1' in model_clean:
            return 'Switch'

        # Check for IR models and PDU/CDU patterns that should be Rack
        ir_rack_models = ['ir9048', 'ir9148', 'ir9149', 'ir7000', 'ir5000']
        for ir_model in ir_rack_models:
            if ir_model in model:
                return 'Rack'

        if 'pdu' in model or 'cdu' in model:
            return 'Rack'

        # PRIORITY 1: Use reference type if item is matched in reference file (HIGH PRIORITY)
        if match_status == 'MATCHED' and ref_type and ref_type != 'none':
            # Map reference types to our categories
            if any(x in ref_type for x in ['switch', 'ethernet switch']):
                return 'Switch'
            elif any(x in ref_type for x in ['transceiver', 'xcvr', 'optic', 'sfp', 'qsfp']):
                return 'Transceiver'
            elif any(x in ref_type for x in ['fiber', 'jumper', 'breakout', 'cable jumper', 'cable']):
                return 'Cables'  # Merged Fiber Cable Jumpers into Cables
            elif any(x in ref_type for x in ['cabling', 'patch cable', 'twisted pair']):
                return 'Cables'
            elif any(x in ref_type for x in ['rack', 'chassis', 'enclosure']):
                return 'Rack'
            elif any(x in ref_type for x in ['pdu', 'power distribution']):
                return 'PDU'
            elif any(x in ref_type for x in ['panel', 'patch', 'shuffle']):
                return 'Panel'

        # PRIORITY 1.5: NVIDIA PN and length-based classification
        # If NVIDIA PN starts with 980, it's a Transceiver (unless it has length info)
        if nvidia_pn and str(nvidia_pn).startswith('980'):
            # But first check if description has length mentions (takes precedence)
            length_patterns = [' m ', ' meter', 'meter ', '50m', '5m', '10m', '25m', '100m', '150m', '300m',
                              '50 m', '5 meter', '10 meter', '25 meter', '100 meter', '150 meter', '300 meter',
                              '50ft', '100ft', '1m', '2m', '3m']
            has_length = any(pattern in desc for pattern in length_patterns)
            if not has_length:
                return 'Transceiver'

        # If description contains length mentions, it's a Cable
        length_patterns = [' m ', ' meter', 'meter ', '50m', '5m', '10m', '25m', '100m', '150m', '300m',
                          '50 m', '5 meter', '10 meter', '25 meter', '100 meter', '150 meter', '300 meter',
                          '50ft', '100ft', '1m', '2m', '3m']
        for pattern in length_patterns:
            if pattern in desc:
                return 'Cables'

        # PRIORITY 2: Smart detection to distinguish Transceiver from Cable
        # Definite Transceivers - module form factors
        transceiver_patterns = [
            'qsfp28', 'qsfp56', 'qsfp-dd', 'qsfp+', 'qsfp',
            'sfp+', 'sfp28', 'sfp-dd', 'sfp',
            'cfp', 'cfp2', 'cfp4',
            'xcvr', 'transceiver', 'optic module',
            'mpo transceiver', 'module'
        ]

        # Definite Cables - not transceiver modules
        cable_patterns = [
            'cat5e', 'cat6a', 'cat6', 'cat7',  # Ethernet cables
            'dac cable', 'dac', 'aoc cable', 'aoc',  # Direct Attach Copper/Optics
            'fiber jumper', 'fiber cable', 'fiber patch',  # Fiber cables
            'mpl8', 'qsfp breakout',  # Breakout cables
            'rj45', 'twisted pair',
            'cbl', 'patch cable', 'jumper cable'
        ]

        # Check model for transceiver indicators
        for pattern in transceiver_patterns:
            if pattern in model:
                return 'Transceiver'

        # Check description for strong cable indicators
        for pattern in cable_patterns:
            if pattern in desc:
                return 'Cables'  # All cable types merged into Cables category

        # Other basic patterns
        if 'switch' in desc or 'switch' in model:
            return 'Switch'
        elif 'rack' in desc or 'chassis' in desc or 'enclosure' in desc:
            return 'Rack'
        elif 'pdu' in desc or 'power distribution' in desc:
            return 'PDU'
        elif 'panel' in desc or 'shuffle' in desc or 'patch' in desc:
            return 'Panel'

        # For unmapped items, use web search
        if match_status == 'UNMAPPED' and model:
            search_result = UnmappedItemSearcher.search_item_type(model, item.get('description', ''))
            if search_result.get('found'):
                category = search_result.get('type', 'Others')

                # Override based on section context
                if 'transceiver' in section or 'xcvr' in section:
                    return 'Transceiver'
                elif 'fiber' in section or ('cable' in section and 'transceiver' not in section):
                    if category == 'Transceiver' and 'fiber' not in section:
                        return 'Transceiver'
                    else:
                        return 'Cables'  # All cable types including fiber

                return category

        # Default categorization based on section
        if 'transceiver' in section or 'xcvr' in section:
            return 'Transceiver'
        elif 'fiber' in section or 'cable' in section:
            return 'Cables'  # All cable types including fiber
        elif 'cable' in section and 'transceiver' not in section:
            return 'Cables'
        elif 'rack' in section or 'pdu' in section or 'cdu' in section:
            return 'Rack'
        elif 'panel' in section or 'shuffle' in section or 'patch' in section:
            return 'Panel'

        return 'Others'

    def get_consolidated(self) -> list:
        """Get consolidated items sorted, EXCLUDING items with total_quantity = 0"""
        items = [item for item in self.consolidated.values() if item['total_quantity'] > 0]
        return sorted(items, key=lambda x: x['total_quantity'], reverse=True)


class ExcelGenerator:
    """Generate consolidated Excel output with corrected metadata rows"""

    def __init__(self, consolidator: Consolidator, metadata: dict = None):
        self.consolidator = consolidator
        self.metadata = metadata or {'customer': '', 'location': '', 'delivery_date': ''}

    def generate(self, output_path: str):
        """Generate Excel file and return the path"""
        print(f"\n💾 Generating Excel output...")

        wb = openpyxl.Workbook()
        wb.remove(wb.active)

        items = self.consolidator.get_consolidated()
        file_names = self.consolidator.all_files

        # Create 3 sheets
        self._create_summary_per_sections(wb, items, file_names)
        self._create_summary_total(wb, items, file_names)
        self._create_summary_comparison(wb, items, file_names)

        wb.save(output_path)
        wb.close()

        print(f"   ✅ Excel file created: {output_path}")
        return output_path

    def _create_summary_per_sections(self, wb, items, file_names):
        """Create Summary per sections sheet"""
        ws = wb.create_sheet('Summary per sections')

        # Row 1: Headers
        headers = ['Section', 'Model/PN', 'NVIDIA Generic Part number', 'Dell PN', 'Description', 'Category']
        headers.extend(file_names)
        headers.append('Total per Section')

        for col_idx, header in enumerate(headers, 1):
            ws.cell(row=1, column=col_idx, value=header)

        # Add metadata rows (Row 2, 3, 4) with labels in column A and values in file columns
        ws['A2'] = 'Customer'
        ws['A3'] = 'Location'
        ws['A4'] = 'Delivery Date'

        file_locations = self.metadata.get('file_locations', {})

        # File data columns start at index 7 (Column G)
        for col_offset, file_name in enumerate(file_names):
            col_idx = 7 + col_offset
            ws.cell(row=2, column=col_idx, value=self.metadata.get('customer', ''))
            ws.cell(row=3, column=col_idx, value=file_locations.get(file_name, ''))
            ws.cell(row=4, column=col_idx, value=self.metadata.get('delivery_date', ''))

        # Row 5+: Data (no empty row)
        row_num = 5

        # Add items grouped by section
        for item in items:
            section = item['section'] or 'Unknown'

            row_data = [
                section,
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
        """Create Summary Total sheet with NVIDIA PN and Dell PN columns"""
        ws = wb.create_sheet('Summary Total')

        # Row 1: Headers
        headers = ['Model/PN', 'Description', 'NVIDIA Generic Part number', 'Dell PN', 'Category']
        headers.extend(file_names)
        headers.append('Total Quantity')

        for col_idx, header in enumerate(headers, 1):
            ws.cell(row=1, column=col_idx, value=header)

        # Add metadata rows (Row 2, 3, 4) with labels in column A and values in file columns
        ws['A2'] = 'Customer'
        ws['A3'] = 'Location'
        ws['A4'] = 'Delivery Date'

        file_locations = self.metadata.get('file_locations', {})

        # File data columns start at index 6 (Column F)
        for col_offset, file_name in enumerate(file_names):
            col_idx = 6 + col_offset
            ws.cell(row=2, column=col_idx, value=self.metadata.get('customer', ''))
            ws.cell(row=3, column=col_idx, value=file_locations.get(file_name, ''))
            ws.cell(row=4, column=col_idx, value=self.metadata.get('delivery_date', ''))

        # Row 5+: Data (no empty row)
        row_num = 5

        # Add items
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

        # Row 1: Headers
        headers = ['Model/PN', 'NVIDIA Generic Part number', 'Dell PN', 'Description', 'Category']
        headers.extend(file_names)
        headers.extend(['Total from File Sections', 'Total from Summary Total Tab', 'Discrepancy', 'Status'])

        for col_idx, header in enumerate(headers, 1):
            ws.cell(row=1, column=col_idx, value=header)

        # Add metadata rows (Row 2, 3, 4) with labels in column A and values in file columns
        ws['A2'] = 'Customer'
        ws['A3'] = 'Location'
        ws['A4'] = 'Delivery Date'

        file_locations = self.metadata.get('file_locations', {})

        # File data columns start at index 6 (Column F)
        for col_offset, file_name in enumerate(file_names):
            col_idx = 6 + col_offset
            ws.cell(row=2, column=col_idx, value=self.metadata.get('customer', ''))
            ws.cell(row=3, column=col_idx, value=file_locations.get(file_name, ''))
            ws.cell(row=4, column=col_idx, value=self.metadata.get('delivery_date', ''))

        # Row 5+: Data (no empty row)
        row_num = 5

        # Add items
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


class BOMConsolidationPipeline:
    """Complete BOM consolidation pipeline"""

    # Location mapping from BOM file names
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

    # Customer name
    CUSTOMER = 'IREN'

    def __init__(self, reference_file, bom_files_dir):
        self.reference_file = reference_file
        self.bom_files_dir = Path(bom_files_dir)
        self.reference_loader = None
        self.consolidator = None
        self.metadata = {'customer': self.CUSTOMER, 'location': '', 'file_locations': {}}

    def extract_location_from_filename(self, filename: str) -> str:
        """Extract location from BOM filename"""
        filename_lower = filename.lower()

        # Check for specific patterns
        for key, location in self.LOCATION_MAP.items():
            if key.lower() in filename_lower:
                return location

        return ''

    def detect_locations(self, bom_files: list):
        """Create mapping of each BOM file to its location"""
        self.metadata['file_locations'] = {}
        for bom_file in bom_files:
            location = self.extract_location_from_filename(bom_file.name)
            self.metadata['file_locations'][bom_file.name] = location or ''

    def run(self, output_file):
        """Run the complete pipeline"""
        print("\n" + "="*80)
        print("NVIDIA L11 BOM CONSOLIDATION - FINAL SOLUTION V2")
        print("="*80)

        # Step 1: Load reference
        self.reference_loader = ReferenceFileLoader(self.reference_file)

        # Step 2: Find BOM files
        bom_files = sorted(self.bom_files_dir.glob('BOM - NETWORK - *.xlsx'))
        print(f"\n🔍 Found {len(bom_files)} BOM files")

        if not bom_files:
            print("❌ No BOM files found!")
            return

        # Step 2.5: Detect locations from BOM file names
        self.detect_locations(bom_files)
        print(f"👤 Customer: {self.metadata['customer']}")
        print(f"📍 Detected Locations: {len(self.metadata['file_locations'])} files")

        # Step 3: Process each BOM file
        self.consolidator = Consolidator()

        for bom_file in bom_files:
            processor = BOMProcessor(bom_file, self.reference_loader)
            items = processor.process()
            if items:
                self.consolidator.add_bom_items(items, bom_file.name)

        # Step 4: Generate output
        generator = ExcelGenerator(self.consolidator, self.metadata)
        output_path = generator.generate(output_file)

        # Step 5: Print summary
        self._print_summary(output_file, output_path)

        return output_path

    def _print_summary(self, output_file, output_path=None):
        """Print consolidation summary with output path"""
        items = self.consolidator.get_consolidated()

        print("\n" + "="*80)
        print("CONSOLIDATION SUMMARY")
        print("="*80)
        print(f"Total unique items: {len(items)}")
        print(f"Total quantity: {sum(item['total_quantity'] for item in items)}")
        print(f"Files processed: {len(self.consolidator.all_files)}")

        # Count by category
        categories = {}
        for item in items:
            cat = item['category']
            if cat not in categories:
                categories[cat] = {'count': 0, 'qty': 0}
            categories[cat]['count'] += 1
            categories[cat]['qty'] += item['total_quantity']

        print(f"\nBy category:")
        for cat in sorted(categories.keys()):
            stats = categories[cat]
            print(f"  {cat:20} | Items: {stats['count']:3} | Qty: {stats['qty']:6}")

        print("\n" + "="*80)
        print(f"📊 OUTPUT FILE CREATED:")
        file_path = output_path or Path(output_file).absolute()
        print(f"📍 {file_path}")
        print("="*80)
        print("✅ Consolidation complete!")


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
        print("Please ensure 'Dell Networking components list details WO Pricing.xlsx' is in the current directory")
        exit(1)

    pipeline = BOMConsolidationPipeline(REFERENCE_FILE, BOM_FILES_DIR)
    pipeline.run(OUTPUT_FILE)
