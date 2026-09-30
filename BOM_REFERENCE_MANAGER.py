"""
BOM Reference File Manager
Manages dynamic reference files for item lookups and enrichment
Supports adding, updating, and versioning reference databases
"""

import json
import openpyxl
import shutil
import logging
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import copy


class ReferenceFileManager:
    """Manages reference files for BOM processing"""

    def __init__(self, config_file="config/reference_sources.json"):
        """Initialize reference manager"""
        self.config_file = Path(config_file)
        self.config = self._load_config()
        self.references = {}
        self.version_history = {}
        self.last_loaded = {}
        self.logger = self._setup_logging()

        # Load initial references
        self._load_all_references()

    def _setup_logging(self):
        """Setup logging"""
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        return logger

    def _load_config(self):
        """Load configuration from JSON"""
        with open(self.config_file, 'r') as f:
            return json.load(f)

    def _save_config(self):
        """Save configuration to JSON"""
        with open(self.config_file, 'w') as f:
            json.dump(self.config, f, indent=2)

    def _load_all_references(self):
        """Load all configured reference databases"""
        self.logger.info("Loading all reference databases...")
        for name, ref_config in self.config['reference_databases'].items():
            if ref_config.get('enabled', True):
                try:
                    self.load_reference(name)
                    self.logger.info(f"✅ Loaded reference: {name}")
                except Exception as e:
                    self.logger.error(f"❌ Failed to load reference {name}: {e}")

    def load_reference(self, name):
        """Load reference data into memory"""
        if name not in self.config['reference_databases']:
            raise ValueError(f"Reference {name} not found in config")

        ref_config = self.config['reference_databases'][name]
        file_path = Path(ref_config['file_path'])

        if not file_path.exists():
            raise FileNotFoundError(f"Reference file not found: {file_path}")

        # Load Excel file
        wb = openpyxl.load_workbook(file_path)

        self.references[name] = {
            'config': ref_config,
            'data': {},
            'loaded_at': datetime.now().isoformat()
        }

        # Parse each sheet
        for sheet_config in ref_config['sheets']:
            sheet_name = sheet_config['name']
            if sheet_name in wb.sheetnames:
                ws = wb[sheet_name]
                self.references[name]['data'][sheet_name] = self._parse_sheet(
                    ws, sheet_config['columns']
                )
                self.logger.info(f"  └─ Loaded sheet: {sheet_name}")

    def _parse_sheet(self, ws, columns):
        """Parse worksheet into normalized data"""
        data = {}
        col_indices = {}

        # Convert column letters to indices
        for col_name, col_letter in columns.items():
            col_indices[col_name] = openpyxl.utils.column_index_from_string(col_letter)

        # Read data rows
        for row_idx, row in enumerate(ws.iter_rows(min_row=2, values_only=False), 2):
            try:
                # Extract values
                values = {}
                for col_name, col_idx in col_indices.items():
                    cell = row[col_idx - 1]
                    values[col_name] = cell.value

                # Skip empty rows
                if not any(values.values()):
                    continue

                # Use model_pn as key
                if 'model_pn' in values and values['model_pn']:
                    key = str(values['model_pn']).lower().replace(' ', '').replace('-', '')
                    data[key] = values

            except Exception as e:
                self.logger.warning(f"Error parsing row {row_idx}: {e}")

        return data

    def add_reference_source(self, name, file_path, sheets_config, description=""):
        """
        Add a new reference database dynamically

        Args:
            name: identifier for this reference
            file_path: location of reference file
            sheets_config: list of sheet definitions with columns mapping
            description: optional description
        """
        if name in self.config['reference_databases']:
            raise ValueError(f"Reference {name} already exists")

        self.config['reference_databases'][name] = {
            'name': name,
            'description': description,
            'file_path': str(file_path),
            'enabled': True,
            'sheets': sheets_config,
            'version': '1.0',
            'added_date': datetime.now().isoformat()
        }

        self.load_reference(name)
        self._save_config()

        self.logger.info(f"✅ Added new reference source: {name}")
        return {'status': 'added', 'name': name}

    def update_reference_source(self, name, file_path=None, sheets_config=None, new_name=None):
        """
        Update an existing reference database
        Backs up old version and tracks version history
        """
        if name not in self.config['reference_databases']:
            raise ValueError(f"Reference {name} not found")

        # Backup current version
        old_config = copy.deepcopy(self.config['reference_databases'][name])
        backup_path = self._create_backup(name, old_config)

        # Update configuration
        if file_path:
            self.config['reference_databases'][name]['file_path'] = str(file_path)
        if sheets_config:
            self.config['reference_databases'][name]['sheets'] = sheets_config
        if new_name:
            self.config['reference_databases'][new_name] = self.config['reference_databases'].pop(name)
            name = new_name

        # Version tracking
        old_version = self.config['reference_databases'][name].get('version', '1.0')
        new_version = self._increment_version(old_version)
        self.config['reference_databases'][name]['version'] = new_version
        self.config['reference_databases'][name]['last_updated'] = datetime.now().isoformat()

        # Reload
        self.load_reference(name)
        self._save_config()

        self.logger.info(f"✅ Updated reference: {name} (v{old_version} → v{new_version})")

        return {
            'status': 'updated',
            'name': name,
            'old_version': old_version,
            'new_version': new_version,
            'backup_path': str(backup_path)
        }

    def find_item(self, query, reference_name=None):
        """
        Search for an item across reference databases

        Args:
            query: search term (model_pn, nvidia_pn, or dell_pn)
            reference_name: specific reference to search (None = all)
        """
        query_normalized = str(query).lower().replace(' ', '').replace('-', '')
        results = []

        # Search in specified or all references
        refs_to_search = {reference_name: self.references[reference_name]} if reference_name else self.references

        for ref_name, ref_data in refs_to_search.items():
            for sheet_name, sheet_data in ref_data['data'].items():
                for key, item in sheet_data.items():
                    if query_normalized == key:
                        results.append({
                            'reference': ref_name,
                            'sheet': sheet_name,
                            'data': item
                        })

        return {
            'query': query,
            'found': len(results) > 0,
            'count': len(results),
            'results': results
        }

    def list_references(self):
        """List all available reference sources"""
        return {
            name: {
                'description': config.get('description', ''),
                'file': config['file_path'],
                'version': config.get('version', '1.0'),
                'sheets': [s['name'] for s in config['sheets']],
                'status': 'loaded' if name in self.references else 'not_loaded',
                'enabled': config.get('enabled', True)
            }
            for name, config in self.config['reference_databases'].items()
        }

    def get_reference_stats(self, reference_name):
        """Get statistics for a reference database"""
        if reference_name not in self.references:
            raise ValueError(f"Reference {reference_name} not loaded")

        ref = self.references[reference_name]
        stats = {
            'reference': reference_name,
            'loaded_at': ref['loaded_at'],
            'sheets': {}
        }

        for sheet_name, sheet_data in ref['data'].items():
            stats['sheets'][sheet_name] = {
                'item_count': len(sheet_data),
                'sample_keys': list(sheet_data.keys())[:5]
            }

        return stats

    def _create_backup(self, name, config):
        """Create backup of reference configuration"""
        backup_dir = Path(self.config['reference_locations']['backup_directory'])
        backup_dir.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_file = backup_dir / f"{name}_v{config.get('version', '1.0')}_{timestamp}.json"

        with open(backup_file, 'w') as f:
            json.dump(config, f, indent=2)

        return backup_file

    def _increment_version(self, version):
        """Increment version string (e.g., 1.0 → 1.1)"""
        parts = version.split('.')
        parts[-1] = str(int(parts[-1]) + 1)
        return '.'.join(parts)

    def print_summary(self):
        """Print summary of loaded references"""
        print("\n" + "="*80)
        print("REFERENCE FILE MANAGER - LOADED REFERENCES")
        print("="*80)

        refs = self.list_references()
        for name, info in refs.items():
            print(f"\n📄 {name}")
            print(f"   Status: {info['status']}")
            print(f"   Version: {info['version']}")
            print(f"   File: {info['file']}")
            print(f"   Sheets: {', '.join(info['sheets'])}")

            if name in self.references:
                stats = self.get_reference_stats(name)
                for sheet_name, sheet_stats in stats['sheets'].items():
                    print(f"     └─ {sheet_name}: {sheet_stats['item_count']} items")

        print("\n" + "="*80 + "\n")


# MAIN EXECUTION
if __name__ == "__main__":
    print("\n📚 Initializing Reference File Manager...\n")

    manager = ReferenceFileManager()
    manager.print_summary()

    # Test search
    print("\n🔍 Testing item search:")
    result = manager.find_item("920-9N62F-00LI-GC1")
    print(f"   Search: {result['query']}")
    print(f"   Found: {result['found']} ({result['count']} matches)")

    if result['results']:
        for r in result['results']:
            print(f"   └─ {r['reference']} → {r['sheet']}")

    print("\n✅ Reference File Manager ready for use!")
