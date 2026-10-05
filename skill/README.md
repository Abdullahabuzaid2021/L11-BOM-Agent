# Claude Skills for L11-BOM-Agent

This folder contains reusable Claude skills to automate and enhance BOM management workflows.

## 📚 Available Skills

### 🔄 BOM Consolidation Wizard

**Location**: `bom-consolidation-wizard/`

An interactive wizard for consolidating multiple Bill of Materials files into a master BOM with automatic GitHub integration.

**What It Does:**
- Discovers and reads multiple BOM files (Excel/XLSX)
- Extracts metadata (customer, location) from filenames
- Maps sections (E-W, N-S, OOB, Scale Out, etc.) from source files
- Intelligently deduplicates components by Model/PN and Description
- Aggregates quantities across all sources
- Updates master BOM file
- Regenerates interactive dashboard
- Auto-commits & pushes to GitHub

**Key Features:**
- ✅ **Interactive Mode** - Step-by-step guidance with user confirmations
- ✅ **Batch Mode** - Automated consolidation for scheduled/daily updates
- ✅ **Smart File Detection** - Auto-detects new files, skips already-processed ones
- ✅ **Change Reports** - Detailed CSV & JSON reports of all changes
- ✅ **GitHub Integration** - Auto-commit with change history
- ✅ **Dashboard Auto-Refresh** - Updates charts and interactive data

**When to Use:**
- Adding new BOM files from suppliers/locations
- Consolidating BOMs from different sources (IREN, Anthropic, NScale, etc.)
- Updating quantities from revised BOM files
- Deduplicating component inventory
- Setting up automated daily BOM consolidations
- Extracting section/category information from multiple BOMs

**Quick Start:**
```
Tell Claude: "I need to consolidate 3 new BOM files into the master"

Claude will guide you through:
1. File discovery
2. Metadata extraction
3. Section mapping
4. Deduplication review
5. Aggregation preview
6. Update & GitHub push
```

**Batch Mode (Automated):**
```bash
python bom-consolidation-wizard/scripts/consolidate_bom.py --batch
```

Use in cron/CI-CD for daily automated consolidations.

**Documentation:**
- `SKILL.md` - Comprehensive skill definition and workflow
- `README.md` - User guide with examples and troubleshooting
- `scripts/consolidate_bom.py` - Core consolidation engine (600+ lines)
- `references/bom_config.yaml` - Configuration template with 30+ mappings
- `evals/evals.json` - Test scenarios and examples

---

## 📋 Skill Structure

Each skill folder contains:

```
skill-name/
├── SKILL.md              # Skill definition & metadata
├── README.md             # User guide & documentation
├── scripts/              # Executable code
│   └── *.py             # Python scripts
├── references/           # Configuration & reference files
│   └── *.yaml           # YAML configs, *.md reference docs
└── evals/               # Test cases & evaluations
    └── evals.json       # Test scenarios
```

---

## 🚀 How to Use a Skill

### Method 1: Install & Use (Recommended)

1. **Install the skill into Claude:**
   - Find the `.skill` file in your downloads
   - Click "Save skill" to install

2. **Use it in Claude:**
   ```
   I need to consolidate my BOMs
   ```
   Claude automatically detects the skill and guides you through the workflow.

### Method 2: Manual Setup

1. **Copy the skill folder** to your project
2. **Configure it** - Edit `references/config.yaml` for your setup
3. **Run it** - Execute the scripts as documented

### Method 3: Integrate with Scripts

```bash
# Interactive mode
python skill/bom-consolidation-wizard/scripts/consolidate_bom.py

# Batch mode (automated)
python skill/bom-consolidation-wizard/scripts/consolidate_bom.py --batch
```

---

## 🛠️ Skill Configuration

Each skill uses a YAML configuration file. For BOM Consolidation:

**File**: `bom-consolidation-wizard/references/bom_config.yaml`

**Key Sections:**
```yaml
# File patterns & locations
source_bom_pattern: "BOMs/*.xlsx"
master_bom_file: "BOM_CONSOLIDATED_FINAL_WITH_SECTIONS.xlsx"

# Column mappings (customize for your Excel structure)
column_mappings:
  model_pn: "A"        # Where is Model/PN in your files?
  description: "B"     # Where is Description?
  
# Section mapping rules (map varied names to unified sections)
section_mappings:
  "Scale Out": "Scale Out Networking"
  "E-W": "E-W Networking"
  "OOB": "OOB Networking"

# GitHub integration
github:
  repo_path: "./L11-BOM-Agent"
  auto_push: true

# Batch mode settings
deduplication:
  auto_threshold: 90   # Auto-approve matches >90% confidence
```

---

## 📊 Skill Capabilities Matrix

| Capability | BOM Consolidation | Notes |
|------------|-------------------|-------|
| Interactive Mode | ✅ | Step-by-step guidance |
| Batch Mode | ✅ | Automated, no user input |
| File Detection | ✅ | Smart new file detection |
| Deduplication | ✅ | Multi-field matching |
| Section Mapping | ✅ | Flexible section hierarchy |
| Dashboard Integration | ✅ | Auto-regenerates charts |
| GitHub Integration | ✅ | Auto-commit & push |
| Change Reports | ✅ | CSV & JSON formats |
| Scheduled Runs | ✅ | Via cron/scheduler |

---

## 🔄 Workflow Examples

### Example 1: Add New Supplier Files
```
User: "I have 3 new Anthropic BOM files to consolidate"

Claude:
1. Discovers the 3 files
2. Extracts metadata (customer=Anthropic, locations from names)
3. Maps sections to existing structure
4. Shows potential duplicates with existing 78 components
5. Asks user to approve merges
6. Updates master BOM
7. Regenerates dashboard
8. Commits & pushes to GitHub
```

### Example 2: Automated Daily Consolidation
```bash
# Setup (one time)
cp bom-consolidation-wizard/references/bom_config.yaml ./
# Customize config with your file paths and mappings

# Schedule it (in crontab)
0 2 * * * cd /path/to/L11-BOM-Agent && python skill/bom-consolidation-wizard/scripts/consolidate_bom.py --batch >> logs/bom.log 2>&1

# Result: Every day at 2am:
# ✓ Detects new BOM files
# ✓ Consolidates them
# ✓ Generates change reports
# ✓ Updates master & dashboard
# ✓ Pushes to GitHub
# ✓ Logs everything
```

### Example 3: One-Time Consolidation from Scratch
```
User: "Consolidate all 19 BOMs from IREN, Anthropic, and NScale into a master file"

Result:
- 78 unique components organized by section
- Metadata extracted from all files
- Sections properly mapped
- GitHub repo initialized with first commit
- Interactive dashboard ready to share
```

---

## 📞 Support & Documentation

**For help with a skill:**

1. **Read the skill's README** - Most common questions answered there
2. **Check SKILL.md** - Detailed workflow and configuration
3. **Review evals/** - See example test cases
4. **Check logs/** - Review session logs for troubleshooting

---

## 🎯 Future Skills

This folder will expand to include additional skills such as:
- [ ] BOM Validation & Quality Checker
- [ ] Component Cost Analyzer
- [ ] Supply Chain Risk Assessor
- [ ] Inventory Optimizer
- [ ] Compliance Validator

---

## 📝 Version History

| Version | Date | Skill | Changes |
|---------|------|-------|---------|
| 1.0 | Oct 2026 | BOM Consolidation Wizard | Initial release with interactive & batch modes |

---

## 🤝 Contributing

To add a new skill to this project:

1. Create a folder: `skill/new-skill-name/`
2. Add the skill structure: `SKILL.md`, `README.md`, `scripts/`, `references/`, `evals/`
3. Document thoroughly in README.md
4. Test with evals.json test cases
5. Update this main README

---

**Questions?** See the specific skill's README or SKILL.md for detailed documentation.
