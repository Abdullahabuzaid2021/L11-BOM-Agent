---
name: bom-consolidation-wizard
description: "Interactive wizard for consolidating multiple Bill of Materials (BOM) files into a master BOM with automatic GitHub integration. Use this skill whenever the user needs to: consolidate new BOM files into a master inventory, add quantities from new source files, extract section/category information from BOM spreadsheets, deduplicate component entries across files, aggregate component data for procurement, or refresh their consolidated BOM with updated quantities. This includes tasks like 'consolidate these BOMs', 'add new files to the master BOM', 'merge quantities from these sheets', 'extract section info from BOMs', 'update the dashboard with new data', or 'aggregate component lists from multiple suppliers/locations'. Works with Excel/spreadsheet files and automates the full workflow: file reading → metadata extraction → deduplication → aggregation → master file update → dashboard regeneration → GitHub commit & push."
---

# BOM Consolidation Wizard

An interactive step-by-step wizard that consolidates multiple Bill of Materials files into a single master BOM with proper deduplication, section mapping, and metadata extraction. Includes automated GitHub integration and dashboard regeneration.

## What This Skill Does

This skill enables you to:
- **Consolidate multiple BOMs** from different suppliers, locations, or customers
- **Extract metadata** (customer, location) from filenames or sheet data
- **Map section information** (E-W Networking, N-S Networking, OOB, etc.) from source files
- **Deduplicate components** using intelligent matching (Model/PN, Description)
- **Aggregate quantities** across all source files
- **Update your master BOM** Excel file automatically
- **Regenerate the dashboard** with new data
- **Commit & push to GitHub** with change history

## When to Use This Skill

Use this skill when you have:
- New BOM files to add to your master consolidation
- Multiple spreadsheets from different sources (suppliers, locations, deployments)
- Component data that needs deduplication and aggregation
- A need to track where components come from and their quantities

The skill is **interactive** — you approve each step before proceeding, ensuring accuracy.

## Two Modes of Operation

### Interactive Mode (Default)
User guides you through each step with confirmations. Best for learning and validating consolidations.

```
I need to consolidate my BOMs
```

### Batch Mode (Automated)
Runs non-interactively from config with auto-approvals. Best for scheduled/daily updates.

```
I want to set up automated daily BOM consolidations
```

Run with: `python consolidate_bom.py --batch`

## The Workflow

The wizard guides you through 6 interactive steps (or runs automatically in batch mode):

### Step 1: File Discovery
- Scan your workspace for BOM files
- Confirm which files to consolidate
- Review file names and preview data

### Step 2: Metadata Extraction
- Extract customer & location from filenames
- Confirm extraction (or manually override)
- Preview the extracted metadata

### Step 3: Section Mapping
- Identify section information from source files
- Map to your unified section names (E-W, N-S, OOB, Scale Out, Racks, etc.)
- Handle new or unknown sections

### Step 4: Deduplication Preview
- Show potential matches (by Model/PN and Description)
- Confirm which items are duplicates
- Handle unmatched items

### Step 5: Aggregation Review
- Preview final consolidated data
- Review quantity totals per component
- Check for any data quality issues

### Step 6: Update & Push
- Update master Excel file
- Regenerate dashboard
- Commit & push to GitHub
- Show change summary

## Configuration

Before running the wizard, ensure you have a configuration file (`bom_config.yaml`) with:

```yaml
# File patterns
source_bom_pattern: "BOMs/*.xlsx"
master_bom_file: "BOM_CONSOLIDATED_FINAL_WITH_SECTIONS.xlsx"

# Column mappings (Excel column letters)
column_mappings:
  model_pn: "A"
  description: "B"
  nvidia_pn: "C"
  dell_pn: "D"
  category: "E"
  section: "F"

# Metadata extraction from filename
metadata:
  pattern: "{customer}_{location}"  # e.g., IREN_Mackenzie.xlsx
  fallback_sheet: "Sheet1"          # If extraction fails, look here

# Section mapping rules
section_mappings:
  "Scale Out": "Scale Out Networking"
  "E-W": "E-W Networking"
  "East-West": "E-W Networking"
  "N-S": "N-S Networking"
  "North-South": "N-S Networking"
  "OOB": "OOB Networking"
  "Racks": "Racks, PDUs, CDUs"
  "Panels": "Patch Panels/Shuffle"

# GitHub integration
github:
  repo_path: "./L11-BOM-Agent"
  commit_message_template: "BOM: Consolidate {files_count} file(s) - {timestamp}"
  auto_push: true

# Dashboard regeneration
dashboard:
  input_file: "BOM_CONSOLIDATED_FINAL_WITH_SECTIONS.xlsx"
  output_file: "BOM_Dashboard_Complete.html"
  regenerate: true
```

## Usage Examples

**Example 1: Add new BOM files to existing master**
```
I have 3 new BOM files from Anthropic that need to be added to the master BOM
```
The wizard will:
1. Find the 3 files
2. Extract metadata (customer=Anthropic, locations from filenames)
3. Map sections to existing structure
4. Deduplicate with existing ~78 components
5. Aggregate quantities
6. Update master and push to GitHub

**Example 2: Consolidate from scratch with multiple sources**
```
I need to consolidate 19 BOM files from IREN, Anthropic, and NScale suppliers
```
The wizard will:
1. Discover all 19 files
2. Extract metadata from filenames
3. Identify section structure in each file
4. Deduplicate across all 19 files
5. Aggregate to final master
6. Create initial GitHub commit

**Example 3: Update quantities only (same files, new quantities)**
```
The Mackenzie site updated their BOMs with new quantities
```
The wizard will:
1. Read updated files
2. Match to existing components
3. Update quantities (deduplication finds existing items)
4. Refresh dashboard
5. Commit & push with message "BOM: Updated quantities from Mackenzie"

## How the Wizard Works

### Step 1: File Discovery
```
Found 3 new BOM files:
  1. Anthropic_Australia.xlsx
  2. Anthropic_Canada.xlsx
  3. Anthropic_US-Cluster1.xlsx

Include all 3 in consolidation? (y/n)
Any files to skip? (enter numbers or 'none')
```

### Step 2: Metadata Extraction
```
Extracted metadata from filenames:
  File: Anthropic_Australia.xlsx
    Customer: Anthropic
    Location: Australia
  
  File: Anthropic_Canada.xlsx
    Customer: Anthropic
    Location: Canada
  
Confirm? (y/n) | Edit? (specify file#)
```

### Step 3: Section Mapping
```
Found sections in source files:
  - "Scale Out RoCE Network BOM" → Scale Out Networking? (y/n)
  - "E-W Switches" → E-W Networking? (y/n)
  - "OOB - Network BOM" → OOB Networking? (y/n)

New sections not in master (handle manually):
  - "Control Plane Networking" → Map to which section?
```

### Step 4: Deduplication
```
Potential duplicates found:

Match Group 1:
  Existing: SN4700 (Model: SN4700, Description: Switch 10GbE)
  New: SN4700 (from Anthropic_Australia.xlsx)
  Quantities: Existing=2, New=3 → Total will be 5
  Deduplicate? (y/n)

Unmatched Items (14):
  - New item from Anthropic: SN5610
  - New item from Anthropic: MQM8700 Transceiver
  
Add as new components? (y/n)
```

### Step 5: Aggregation Review
```
Consolidation Summary:
  Total components in master: 78
  New components added: 12
  Existing components updated: 22
  Total unique components: 90
  
  Component count by section:
    Scale Out Networking: 31 (+2)
    N-S Networking: 27
    Racks, PDUs, CDUs: 7
    OOB Networking: 6
    Patch Panels/Shuffle: 5
    E-W Networking: 4

Proceed with update? (y/n)
```

### Step 6: Update & Push
```
✓ Master BOM updated (BOM_CONSOLIDATED_FINAL_WITH_SECTIONS.xlsx)
✓ Dashboard regenerated (BOM_Dashboard_Complete.html)
✓ GitHub commit created
✓ Changes pushed to remote

Change Summary:
  Files consolidated: 3
  New components: 12
  Updated components: 22
  Commit: abc1234
  Message: BOM: Consolidate 3 file(s) from Anthropic locations - 2026-10-05
  
  Dashboard updated:
    https://abdullahabuzaid2021.github.io/L11-BOM-Agent/dashboard/
    (Changes visible in ~30 seconds)
```

## ✨ Enhanced Features (v1.1)

### Smart File Detection
The wizard tracks which files have been processed before, automatically detecting new ones:
```
File Status:
  New files (not yet consolidated): 3
    + Anthropic_Australia.xlsx
    + Anthropic_Canada.xlsx
    + Anthropic_US-Cluster1.xlsx
  
  Previously consolidated: 16
    (Quantities will be updated)
```

Prevents re-processing the same files and speeds up future consolidations.

### Batch Mode for Automation
Run non-interactively for scheduled/daily consolidations:

```bash
# Run batch consolidation (reads config, auto-approves high-confidence matches)
python consolidate_bom.py --batch

# Use in cron/scheduled task for daily updates
0 2 * * * cd /path/to/BOMs && python consolidate_bom.py --batch >> logs/consolidation.log 2>&1
```

Benefits:
- No user interaction required
- High-confidence deduplication auto-approved (>90% match)
- Consistent, repeatable consolidations
- Detailed logs for auditing
- Perfect for team workflows

### Detailed Change Reports
Generates both CSV and JSON reports showing exactly what changed:

**CSV Report** (`CONSOLIDATION_CHANGES_20261005_120000.csv`)
```
NEW COMPONENTS
Model/PN,Description,Quantity
SN5610,Switch (Spine),10
MQM8700,Transceiver,50

MERGED DUPLICATES
Model/PN,Old Qty,New Qty,Combined Qty
SN4700,2,3,5
RGH100,4,6,10
```

**JSON Report** (`CONSOLIDATION_CHANGES_20261005_120000.json`)
```json
{
  "timestamp": "2026-10-05T12:00:00",
  "summary": {
    "new_components": 12,
    "merged_duplicates": 22,
    "skipped_files": 0
  },
  "details": {
    "new_components": [...],
    "merged_duplicates": [...],
    "skipped_files": []
  }
}
```

Use these for:
- Procurement planning (new items to order)
- Inventory updates (merged quantities)
- Audit trails (what changed and when)
- Team communication (change summaries)

---

## What Gets Updated

### Master BOM File (Excel)
- **Summary per sections** tab: 90 components (was 78)
- **Summary Total** tab: Updated quantities
- **Summary total comparison** tab: Shows deltas from previous

### Dashboard
- All charts reflect new data
- Filters include new components
- CSV export includes latest info

### GitHub
- New commit with change summary
- File history preserved
- All changes auditable

## Success Criteria

After the wizard completes:
1. ✓ Master BOM file updated with all new components & quantities
2. ✓ Dashboard shows updated data (charts, tables, exports)
3. ✓ GitHub repo has new commit documenting changes
4. ✓ All deduplication decisions logged (for audit trail)
5. ✓ No data loss (original files unchanged)

## Troubleshooting

**Problem: Metadata extraction fails for some files**
- Files don't follow naming pattern
- Solution: Wizard will prompt for manual entry during Step 2

**Problem: Section mapping unclear (new sections found)**
- Source files have sections not in master
- Solution: Wizard shows all new sections and prompts for mapping

**Problem: Too many deduplication matches**
- Component descriptions vary across suppliers
- Solution: Review each match in Step 4; skip uncertain ones

**Problem: GitHub push fails**
- Network issue or authentication problem
- Solution: Wizard saves all changes locally first; retry push separately

## Under the Hood

The wizard uses:
- **openpyxl** - Read/write Excel files
- **Python regex** - Pattern matching for metadata & sections
- **Git CLI** - Version control integration
- **Chart.js** - Dashboard regeneration from data

All operations are reversible — failed pushes don't update local files, and the wizard keeps backups of original master before updating.

## Running the Wizard

```bash
python bom_consolidation_wizard.py \
  --config bom_config.yaml \
  --master BOM_CONSOLIDATED_FINAL_WITH_SECTIONS.xlsx
```

Or directly via Claude:
```
I need to consolidate my BOMs. Let's start the wizard.
```

The skill will:
1. Check your workspace for config & files
2. Guide you through 6 interactive steps
3. Handle all consolidation logic
4. Update files & push to GitHub
5. Show final change summary
