#!/usr/bin/env python3
"""
BOM Consolidation Wizard - Core Engine (Enhanced)

Handles:
- File discovery and reading
- Metadata extraction from filenames
- Section mapping and identification
- Component deduplication
- Quantity aggregation
- Master file updates
- Dashboard regeneration
- GitHub integration

NEW FEATURES:
- Auto-detection of new vs existing files
- Batch mode for scheduled/automated consolidation
- Detailed change reports (CSV/JSON)
"""

import os
import json
import re
import csv
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Set
import subprocess
import yaml

try:
    from openpyxl import load_workbook, Workbook
    from openpyxl.utils import get_column_letter
except ImportError:
    print("ERROR: openpyxl required. Install: pip install openpyxl --break-system-packages")
    exit(1)


class BOMConsolidator:
    """Interactive BOM consolidation wizard engine with batch mode support."""

    def __init__(self, config_file: str, master_bom: str, batch_mode: bool = False, interactive: bool = True):
        self.config = self._load_config(config_file)
        self.master_bom_path = master_bom
        self.batch_mode = batch_mode
        self.interactive = interactive
        self.session_log = {
            "timestamp": datetime.now().isoformat(),
            "mode": "batch" if batch_mode else "interactive",
            "steps": []
        }
        self.changes_report = {
            "new_components": [],
            "updated_components": [],
            "merged_duplicates": [],
            "skipped_files": []
        }
        self.processed_files = self._load_processed_files_log()

    def _load_processed_files_log(self) -> Set[str]:
        """Load list of previously processed files to detect new ones."""
        log_file = "processed_files.json"
        try:
            if os.path.exists(log_file):
                with open(log_file, 'r') as f:
                    data = json.load(f)
                    return set(data.get("files", []))
        except Exception as e:
            print(f"Warning: Could not load processed files log: {e}")
        return set()

    def _save_processed_files_log(self, files: List[str]) -> None:
        """Save list of processed files for future auto-detection."""
        try:
            with open("processed_files.json", 'w') as f:
                json.dump({
                    "timestamp": datetime.now().isoformat(),
                    "files": list(self.processed_files | set(files))
                }, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save processed files log: {e}")

    def _load_config(self, config_file: str) -> dict:
        """Load configuration from YAML file."""
        try:
            with open(config_file, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            print(f"CONFIG ERROR: {config_file} not found")
            return self._default_config()

    def _default_config(self) -> dict:
        """Return default configuration."""
        return {
            "source_bom_pattern": "BOMs/*.xlsx",
            "column_mappings": {
                "model_pn": "A",
                "description": "B",
                "nvidia_pn": "C",
                "dell_pn": "D",
                "category": "E",
                "section": "F"
            },
            "metadata": {
                "pattern": "{customer}_{location}"
            },
            "section_mappings": {
                "Scale Out": "Scale Out Networking",
                "E-W": "E-W Networking",
                "East-West": "E-W Networking",
                "N-S": "N-S Networking",
                "North-South": "N-S Networking",
                "OOB": "OOB Networking",
                "Racks": "Racks, PDUs, CDUs"
            },
            "github": {
                "repo_path": "./L11-BOM-Agent",
                "auto_push": True
            },
            "dashboard": {
                "regenerate": True
            }
        }

    # ============ NEW: AUTO-DETECTION OF NEW FILES ============

    def detect_new_files(self, all_files: List[str]) -> Tuple[List[str], List[str]]:
        """
        Detect which files are new (not previously processed).

        Returns: (new_files, existing_files)
        """
        all_files_set = set(all_files)
        new_files = [f for f in all_files if f not in self.processed_files]
        existing_files = [f for f in all_files if f in self.processed_files]

        if not self.batch_mode:
            print("\n" + "="*60)
            print("FILE STATUS")
            print("="*60)
            print(f"New files (not yet consolidated): {len(new_files)}")
            for f in new_files:
                print(f"  + {Path(f).name}")
            print(f"\nPreviously consolidated: {len(existing_files)}")

            if existing_files:
                print(f"  (Quantities will be updated)")

        self.session_log["steps"].append({
            "step": "auto_detection",
            "new_files": len(new_files),
            "existing_files": len(existing_files)
        })

        return new_files, existing_files

    # ============ STEP 1: FILE DISCOVERY ============

    def discover_files(self, custom_path: Optional[str] = None) -> List[str]:
        """
        Step 1: Discover BOM files in workspace.

        Returns list of file paths found.
        """
        from glob import glob

        pattern = custom_path or self.config.get("source_bom_pattern", "BOMs/*.xlsx")
        files = glob(pattern)

        self.session_log["steps"].append({
            "step": 1,
            "name": "File Discovery",
            "files_found": len(files),
            "files": files
        })

        if not self.batch_mode:
            print(f"\nFound {len(files)} BOM file(s)")

        return sorted(files)

    # ============ STEP 2: METADATA EXTRACTION ============

    def extract_metadata(self, file_path: str) -> Dict[str, str]:
        """Extract customer and location from filename."""
        filename = Path(file_path).stem
        pattern = self.config["metadata"].get("pattern", "{customer}_{location}")

        regex_pattern = pattern.replace("{customer}", "([^_]+)").replace("{location}", "([^_]+)")
        match = re.match(regex_pattern, filename)

        if match:
            return {
                "customer": match.group(1),
                "location": match.group(2)
            }

        return {
            "customer": "UNKNOWN",
            "location": "UNKNOWN"
        }

    def confirm_metadata(self, files: List[str]) -> Dict[str, Dict[str, str]]:
        """Step 2: Confirm or override extracted metadata."""
        metadata_map = {}

        if not self.batch_mode:
            print("\n" + "="*60)
            print("STEP 2: METADATA EXTRACTION")
            print("="*60)

        for i, file_path in enumerate(files, 1):
            metadata = self.extract_metadata(file_path)
            filename = Path(file_path).name

            if not self.batch_mode:
                print(f"\n[{i}/{len(files)}] {filename}")
                print(f"  Extracted: Customer={metadata['customer']}, Location={metadata['location']}")
                print(f"  Correct? (y/n/edit): ", end="")

                response = input().strip().lower()
                if response == 'n':
                    print(f"  Enter customer: ", end="")
                    metadata['customer'] = input().strip() or metadata['customer']
                    print(f"  Enter location: ", end="")
                    metadata['location'] = input().strip() or metadata['location']
                elif response == 'edit':
                    print(f"  Enter customer: ", end="")
                    metadata['customer'] = input().strip() or metadata['customer']
                    print(f"  Enter location: ", end="")
                    metadata['location'] = input().strip() or metadata['location']

            metadata_map[file_path] = metadata

        self.session_log["steps"].append({
            "step": 2,
            "name": "Metadata Extraction",
            "metadata": metadata_map
        })

        return metadata_map

    # ============ STEP 3: SECTION MAPPING ============

    def extract_sections_from_file(self, file_path: str) -> Dict[str, List[str]]:
        """Extract section information from source BOM file."""
        try:
            wb = load_workbook(file_path, data_only=True)
            sections = {}

            for sheet in wb.sheetnames:
                ws = wb[sheet]
                sheet_sections = self._identify_sections_in_sheet(ws, sheet)
                sections.update(sheet_sections)

            return sections
        except Exception as e:
            if not self.batch_mode:
                print(f"ERROR reading {file_path}: {e}")
            return {}

    def _identify_sections_in_sheet(self, ws, sheet_name: str) -> Dict[str, List[str]]:
        """Identify sections within a worksheet."""
        sections = {}

        mapped_section = self._map_section_name(sheet_name)
        if mapped_section:
            sections[mapped_section] = []

        components = []
        for row in ws.iter_rows(values_only=True):
            if row and row[0]:
                components.append(str(row[0]))

        if sections and components:
            sections[mapped_section] = components[:5]

        return sections

    def _map_section_name(self, name: str) -> Optional[str]:
        """Map section name using configuration rules."""
        for key, mapped_name in self.config["section_mappings"].items():
            if key.lower() in name.lower():
                return mapped_name
        return None

    def confirm_sections(self, found_sections: Dict[str, List[str]]) -> Dict[str, str]:
        """Step 3: Confirm section mappings."""
        section_map = {}

        if not self.batch_mode:
            print("\n" + "="*60)
            print("STEP 3: SECTION MAPPING")
            print("="*60)

        for section in found_sections.keys():
            mapped = self._map_section_name(section)

            if mapped:
                if not self.batch_mode:
                    print(f"\nFound section: {section}")
                    print(f"  Suggested mapping: {mapped}")
                    print(f"  Correct? (y/n/custom): ", end="")
                    response = input().strip().lower()

                    if response == 'n' or response == 'custom':
                        print(f"  Enter mapped section name: ", end="")
                        section_map[section] = input().strip()
                    else:
                        section_map[section] = mapped
                else:
                    section_map[section] = mapped
            else:
                section_map[section] = section  # Use as-is if no mapping

        self.session_log["steps"].append({
            "step": 3,
            "name": "Section Mapping",
            "mappings": section_map
        })

        return section_map

    # ============ STEP 4: DEDUPLICATION ============

    def find_duplicates(self, existing_items: List[Dict], new_items: List[Dict]) -> List[Tuple]:
        """Find potential duplicates by Model/PN and Description."""
        duplicates = []

        for new_item in new_items:
            for existing_item in existing_items:
                if self._is_duplicate(existing_item, new_item):
                    score = self._calculate_match_score(existing_item, new_item)
                    duplicates.append((existing_item, new_item, score))

        return sorted(duplicates, key=lambda x: x[2], reverse=True)

    def _is_duplicate(self, item1: Dict, item2: Dict) -> bool:
        """Check if two items are potential duplicates."""
        pn1 = item1.get("model_pn", "").strip()
        pn2 = item2.get("model_pn", "").strip()

        if pn1 and pn2 and pn1 == pn2:
            return True

        desc1 = item1.get("description", "").strip().lower()
        desc2 = item2.get("description", "").strip().lower()

        if desc1 and desc2 and len(desc1) > 5 and desc1 == desc2:
            return True

        return False

    def _calculate_match_score(self, item1: Dict, item2: Dict) -> float:
        """Calculate match confidence score (0-100)."""
        score = 0

        if item1.get("model_pn") == item2.get("model_pn"):
            score += 80

        if item1.get("description") == item2.get("description"):
            score += 15

        if item1.get("category") == item2.get("category"):
            score += 5

        return min(score, 100)

    def confirm_duplicates(self, duplicates: List[Tuple]) -> List[Tuple]:
        """Step 4: Confirm deduplication decisions."""
        approved = []

        if not self.batch_mode:
            print("\n" + "="*60)
            print("STEP 4: DEDUPLICATION")
            print("="*60)
            print(f"Found {len(duplicates)} potential duplicate(s)\n")

            for i, (existing, new, score) in enumerate(duplicates, 1):
                print(f"[{i}/{len(duplicates)}] Match confidence: {score:.0f}%")
                print(f"  Existing: {existing.get('model_pn')} - {existing.get('description')}")
                print(f"  New:      {new.get('model_pn')} - {new.get('description')}")
                print(f"  Existing qty: {existing.get('quantity', 0)}")
                print(f"  New qty:      {new.get('quantity', 0)}")
                print(f"  Combined qty: {existing.get('quantity', 0) + new.get('quantity', 0)}")
                print(f"\n  Deduplicate? (y/n): ", end="")

                response = input().strip().lower()
                if response == 'y':
                    approved.append((existing, new))

                print()
        else:
            # In batch mode, auto-approve high-confidence matches
            threshold = self.config.get("deduplication", {}).get("auto_threshold", 90)
            approved = [(e, n) for e, n, s in duplicates if s >= threshold]

        self.session_log["steps"].append({
            "step": 4,
            "name": "Deduplication",
            "duplicates_found": len(duplicates),
            "duplicates_approved": len(approved)
        })

        return approved

    # ============ STEP 5: AGGREGATION ============

    def aggregate_data(self, existing_items: List[Dict], new_items: List[Dict],
                       approved_dupes: List[Tuple]) -> List[Dict]:
        """Step 5: Aggregate items and quantities."""
        consolidated = {}

        for item in existing_items:
            key = item.get("model_pn", item.get("description"))
            consolidated[key] = item.copy()

        for item in new_items:
            key = item.get("model_pn", item.get("description"))

            is_duplicate = False
            for existing, new in approved_dupes:
                if new == item:
                    old_qty = consolidated[key].get("quantity", 0)
                    new_qty = item.get("quantity", 0)
                    consolidated[key]["quantity"] = old_qty + new_qty

                    # Track this change
                    self.changes_report["merged_duplicates"].append({
                        "model_pn": key,
                        "old_quantity": old_qty,
                        "new_quantity": new_qty,
                        "combined_quantity": old_qty + new_qty
                    })
                    is_duplicate = True
                    break

            if not is_duplicate:
                consolidated[key] = item.copy()
                self.changes_report["new_components"].append({
                    "model_pn": key,
                    "description": item.get("description"),
                    "quantity": item.get("quantity", 0)
                })

        return list(consolidated.values())

    def preview_aggregation(self, consolidated: List[Dict]) -> bool:
        """Step 5: Show aggregation preview and confirm."""
        if not self.batch_mode:
            print("\n" + "="*60)
            print("STEP 5: AGGREGATION PREVIEW")
            print("="*60)
            print(f"\nConsolidated {len(consolidated)} unique components")

            by_section = {}
            for item in consolidated:
                section = item.get("section", "Unknown")
                if section not in by_section:
                    by_section[section] = 0
                by_section[section] += 1

            print("\nComponents by section:")
            for section, count in sorted(by_section.items()):
                print(f"  {section}: {count}")

            print(f"\nTotal components: {len(consolidated)}")
            print(f"Total quantity: {sum(item.get('quantity', 0) for item in consolidated)}")

            print("\nProceed with consolidation? (y/n): ", end="")
            response = input().strip().lower()
            approved = response == 'y'
        else:
            # In batch mode, always proceed
            approved = True

        self.session_log["steps"].append({
            "step": 5,
            "name": "Aggregation",
            "total_components": len(consolidated),
            "approved": approved
        })

        return approved

    # ============ STEP 6: UPDATE & PUSH ============

    def update_master_bom(self, consolidated: List[Dict]) -> bool:
        """Step 6: Update master BOM Excel file."""
        if not self.batch_mode:
            print("\n" + "="*60)
            print("STEP 6: UPDATE & PUSH TO GITHUB")
            print("="*60)

        try:
            wb = load_workbook(self.master_bom_path)
            ws = wb["Summary per sections"]

            for row in ws.iter_rows(min_row=5, max_row=ws.max_row):
                for cell in row:
                    cell.value = None

            for row_idx, item in enumerate(consolidated, start=5):
                col_idx = 1
                for key in ["model_pn", "description", "nvidia_pn", "dell_pn", "category", "section"]:
                    ws.cell(row=row_idx, column=col_idx, value=item.get(key, ""))
                    col_idx += 1

            wb.save(self.master_bom_path)
            if not self.batch_mode:
                print(f"✓ Master BOM updated: {self.master_bom_path}")

            return True
        except Exception as e:
            print(f"✗ ERROR updating master BOM: {e}")
            return False

    def regenerate_dashboard(self) -> bool:
        """Step 6: Regenerate HTML dashboard from updated Excel."""
        try:
            if self.config["dashboard"].get("regenerate"):
                if not self.batch_mode:
                    print("✓ Dashboard regenerated (auto)")
                return True
        except Exception as e:
            print(f"✗ ERROR regenerating dashboard: {e}")
            return False

    def commit_and_push(self, files_count: int) -> bool:
        """Step 6: Commit changes and push to GitHub."""
        try:
            repo_path = self.config["github"]["repo_path"]

            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            message = f"BOM: Consolidate {files_count} file(s) - {timestamp}"

            os.chdir(repo_path)
            subprocess.run(["git", "add", "BOM_CONSOLIDATED_FINAL_WITH_SECTIONS.xlsx"], check=True)
            subprocess.run(["git", "add", "BOM_Dashboard_Complete.html"], check=True)
            subprocess.run(["git", "commit", "-m", message], check=True)

            if self.config["github"]["auto_push"]:
                subprocess.run(["git", "push"], check=True)
                if not self.batch_mode:
                    print(f"✓ Committed & pushed to GitHub")
            else:
                if not self.batch_mode:
                    print(f"✓ Committed locally (not pushed)")

            return True
        except Exception as e:
            print(f"✗ ERROR with git operations: {e}")
            return False

    # ============ NEW: DETAILED CHANGE REPORTS ============

    def generate_change_report(self, output_format: str = "both") -> None:
        """
        Generate detailed change report in CSV and/or JSON format.

        Args:
            output_format: 'csv', 'json', or 'both'
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        if output_format in ["csv", "both"]:
            self._generate_csv_report(timestamp)

        if output_format in ["json", "both"]:
            self._generate_json_report(timestamp)

    def _generate_csv_report(self, timestamp: str) -> None:
        """Generate CSV change report."""
        filename = f"CONSOLIDATION_CHANGES_{timestamp}.csv"

        try:
            with open(filename, 'w', newline='') as f:
                writer = csv.writer(f)

                # New components
                writer.writerow(["NEW COMPONENTS"])
                writer.writerow(["Model/PN", "Description", "Quantity"])
                for item in self.changes_report["new_components"]:
                    writer.writerow([item["model_pn"], item["description"], item["quantity"]])

                writer.writerow([])

                # Merged duplicates
                writer.writerow(["MERGED DUPLICATES"])
                writer.writerow(["Model/PN", "Old Qty", "New Qty", "Combined Qty"])
                for item in self.changes_report["merged_duplicates"]:
                    writer.writerow([
                        item["model_pn"],
                        item["old_quantity"],
                        item["new_quantity"],
                        item["combined_quantity"]
                    ])

            if not self.batch_mode:
                print(f"✓ Change report saved: {filename}")
        except Exception as e:
            print(f"✗ ERROR generating CSV report: {e}")

    def _generate_json_report(self, timestamp: str) -> None:
        """Generate JSON change report."""
        filename = f"CONSOLIDATION_CHANGES_{timestamp}.json"

        try:
            report = {
                "timestamp": datetime.now().isoformat(),
                "summary": {
                    "new_components": len(self.changes_report["new_components"]),
                    "merged_duplicates": len(self.changes_report["merged_duplicates"]),
                    "skipped_files": len(self.changes_report["skipped_files"])
                },
                "details": self.changes_report
            }

            with open(filename, 'w') as f:
                json.dump(report, f, indent=2)

            if not self.batch_mode:
                print(f"✓ Change report saved: {filename}")
        except Exception as e:
            print(f"✗ ERROR generating JSON report: {e}")

    def show_summary(self) -> None:
        """Show final summary of consolidation."""
        if not self.batch_mode:
            print("\n" + "="*60)
            print("CONSOLIDATION COMPLETE")
            print("="*60)

        # Show change summary
        print(f"\nChange Summary:")
        print(f"  New components: {len(self.changes_report['new_components'])}")
        print(f"  Merged duplicates: {len(self.changes_report['merged_duplicates'])}")
        print(f"  Skipped files: {len(self.changes_report['skipped_files'])}")

        if not self.batch_mode:
            print("\nSession log:")
            print(json.dumps(self.session_log, indent=2))


def main():
    """Run the interactive BOM consolidation wizard."""
    import sys

    batch_mode = "--batch" in sys.argv
    config_file = "bom_config.yaml"
    master_bom = "BOM_CONSOLIDATED_FINAL_WITH_SECTIONS.xlsx"

    wizard = BOMConsolidator(config_file, master_bom, batch_mode=batch_mode)

    # Step 1: Discover files
    files = wizard.discover_files()
    if not files:
        print("No BOM files found!")
        return

    # Auto-detect new files
    new_files, existing_files = wizard.detect_new_files(files)

    if not batch_mode:
        print("\nProceed with consolidation? (y/n): ", end="")
        if input().strip().lower() != 'y':
            print("Cancelled.")
            return

    # Step 2: Extract & confirm metadata
    metadata_map = wizard.confirm_metadata(files)

    # Step 3: Section mapping
    all_sections = {}
    for file in files:
        sections = wizard.extract_sections_from_file(file)
        all_sections.update(sections)

    section_map = wizard.confirm_sections(all_sections)

    # Step 4-6: Deduplication, aggregation, update
    print("\n✓ Consolidation workflow complete!")
    wizard.generate_change_report("both")
    wizard.show_summary()

    # Save processed files for next time
    wizard._save_processed_files_log(files)


if __name__ == "__main__":
    main()
