# BOM Consolidation Wizard - Skill

An interactive skill for consolidating multiple Bill of Materials (BOM) files into a single master BOM with automatic GitHub integration and dashboard regeneration.

## 🎯 What This Skill Does

Automates the entire BOM consolidation workflow:

1. **Discovers** multiple BOM files from your workspace
2. **Extracts metadata** (customer, location) from filenames
3. **Maps sections** (E-W, N-S, OOB, etc.) from source files  
4. **Deduplicates** components intelligently
5. **Aggregates** quantities across all sources
6. **Updates** master BOM Excel file
7. **Regenerates** interactive dashboard
8. **Commits & pushes** to GitHub automatically

## 📋 Requirements

### Files Needed
- `bom_config.yaml` - Configuration file (see references/)
- `BOM_CONSOLIDATED_FINAL_WITH_SECTIONS.xlsx` - Master BOM to update
- Source BOM files in `BOMs/` folder (or custom path)

### Dependencies
```bash
pip install openpyxl pyyaml --break-system-packages
```

### Git Setup
- Repository initialized with git (`git init`)
- Remote configured (`git remote add origin ...`)
- Credentials configured for push operations

## 🚀 Quick Start

### 1. Set Up Configuration

Copy the provided `bom_config.yaml` to your project root:

```bash
cp references/bom_config.yaml ./bom_config.yaml
```

Edit to match your setup:
- Update file paths
- Adjust column mappings if different
- Add your section mappings
- Set GitHub repo path

### 2. Prepare Your BOMs

Organize source files in a folder (default: `BOMs/`):

```
BOMs/
├── IREN_Mackenzie.xlsx
├── IREN_Childress.xlsx
├── Anthropic_Australia.xlsx
├── Anthropic_Canada.xlsx
└── NScale_Narvik.xlsx
```

**Filename pattern**: `{customer}_{location}.xlsx`

### 3. Run the Wizard

Tell Claude to use the skill:

```
I need to consolidate all my BOM files. Let's start the consolidation wizard.
```

Or provide specific files:

```
I have 3 new Anthropic BOM files that need to be added to the master consolidation.
```

The skill will:
- Guide you through 6 interactive steps
- Ask for confirmation at each step
- Update files automatically
- Push to GitHub

## 📊 How It Works

### Step 1: File Discovery
```
Found 5 BOM files:
  1. IREN_Mackenzie.xlsx
  2. IREN_Childress.xlsx
  3. Anthropic_Australia.xlsx
  4. Anthropic_Canada.xlsx
  5. NScale_Narvik.xlsx

Include all 5 in consolidation? (y/n)
```

### Step 2: Metadata Extraction
```
Extracted metadata from filenames:
  File: Anthropic_Australia.xlsx
    Customer: Anthropic
    Location: Australia

Confirm? (y/n)
```

### Step 3: Section Mapping
```
Found sections in source files:
  - "Scale Out RoCE Network BOM" → Scale Out Networking? (y/n)
  - "E-W Switches" → E-W Networking? (y/n)
  
New sections not in master:
  - "Custom_Section" → Map to which section?
```

### Step 4: Deduplication
```
Potential duplicates found:

Match Group 1:
  Existing: SN4700 (Switch 10GbE)
  New: SN4700 (from Anthropic_Australia.xlsx)
  Quantities: Existing=2, New=3 → Total will be 5
  Deduplicate? (y/n)
```

### Step 5: Aggregation Preview
```
Consolidation Summary:
  Total components in master: 78
  New components added: 12
  Existing components updated: 22
  Total unique components: 90
  
  Component count by section:
    Scale Out Networking: 31 (+2)
    N-S Networking: 27
    ...

Proceed with update? (y/n)
```

### Step 6: Update & Push
```
✓ Master BOM updated
✓ Dashboard regenerated
✓ GitHub commit created
✓ Changes pushed to remote

Dashboard URL:
https://abdullahabuzaid2021.github.io/L11-BOM-Agent/dashboard/
(Live in ~30 seconds)
```

## 🔧 Configuration Reference

### Column Mappings
Customize where your data lives in the Excel files:

```yaml
column_mappings:
  model_pn: "A"        # Part number
  description: "B"     # Component name
  nvidia_pn: "C"       # NVIDIA part number
  dell_pn: "D"         # Dell part number
  category: "E"        # Component type
  section: "F"         # Network section
```

### Section Mappings
Define how section names from source files map to unified names:

```yaml
section_mappings:
  "Scale Out": "Scale Out Networking"
  "E-W": "E-W Networking"
  "N-S": "N-S Networking"
  "OOB": "OOB Networking"
```

### GitHub Integration
Control how changes are committed and pushed:

```yaml
github:
  repo_path: "./L11-BOM-Agent"
  auto_push: true          # Automatically push after commit
  create_tag: false        # Tag major releases
```

### Dashboard Regeneration
Automatically refresh the interactive dashboard:

```yaml
dashboard:
  regenerate: true
  input_file: "BOM_CONSOLIDATED_FINAL_WITH_SECTIONS.xlsx"
  output_file: "BOM_Dashboard_Complete.html"
```

## 📚 What Gets Updated

### Master BOM File
- **Summary per sections** tab: All components organized by section
- **Summary Total** tab: Complete consolidated inventory
- **Summary total comparison** tab: Changes from previous version

All existing data preserved — only adds new items and updates quantities.

### Dashboard
- Charts reflect updated data
- Filters show new components
- CSV exports include latest info
- Live at GitHub Pages URL

### GitHub
- New commit with change summary
- Timestamp in message
- All files tracked for audit trail
- Easy to revert if needed

## ⚙️ Troubleshooting

### Metadata Extraction Fails
**Problem**: Filenames don't match expected pattern

**Solution**: 
- Edit filenames to match pattern: `{customer}_{location}.xlsx`
- Or confirm metadata manually during Step 2

### Section Mapping Unclear
**Problem**: Source files have sections not in your unified list

**Solution**: 
- Wizard will prompt for mapping during Step 3
- Add new sections to `section_mappings` in config

### Deduplication Too Aggressive
**Problem**: Wizard is marking non-duplicates as matching

**Solution**:
- Review each potential match during Step 4
- Only approve matches you're confident about
- Unmatched items are added as new components

### GitHub Push Fails
**Problem**: Authentication error or network issue

**Solution**:
1. Check git is configured: `git config --list`
2. Test authentication: `git push origin main --dry-run`
3. Wizard saves changes locally — retry push manually later

## 📁 File Structure

```
bom-consolidation-wizard/
├── SKILL.md                          # Skill definition (main)
├── README.md                         # This file
├── scripts/
│   └── consolidate_bom.py           # Core consolidation engine
├── references/
│   └── bom_config.yaml              # Configuration template
└── evals/
    └── evals.json                   # Test cases
```

## 🔍 Understanding the Consolidation Process

### Deduplication Logic

Items are considered duplicates if:
1. **Model/PN matches exactly** (highest confidence)
2. **Description matches exactly** (secondary match)
3. **NVIDIA PN matches** (tertiary match)

When duplicates are found:
- Quantities are **summed** together
- Existing item retains all metadata
- Source file is recorded for audit trail

### Metadata Extraction

By default, expects filenames like:
```
{customer}_{location}.xlsx
IREN_Mackenzie.xlsx       → customer=IREN, location=Mackenzie
Anthropic_Australia.xlsx  → customer=Anthropic, location=Australia
NScale_Narvik_8k.xlsx     → customer=NScale, location=Narvik_8k
```

Can be customized in `bom_config.yaml`:
```yaml
metadata:
  pattern: "{customer}_{location}"  # Or any other pattern
```

### Section Mapping

Source files can specify sections in multiple ways:
- **Sheet names**: `"E-W Switches"` tab → E-W Networking
- **Table headers**: Row with `"Scale Out RoCE"` 
- **Cell values**: Specific cells containing section names

Wizard identifies all sections and maps to unified names using config rules.

## 📝 Session Logging

Each consolidation session creates:

1. **`consolidation_sessions.json`** - Full session log
2. **`CONSOLIDATION_AUDIT_{timestamp}.csv`** - Deduplication decisions
3. **`REFERENCE_LIST_{timestamp}.csv`** - Source→component mapping

Use these for:
- Auditing what changed
- Understanding deduplication decisions
- Tracking history over time

## 🎯 Success Checklist

After running the wizard, verify:

- [ ] Master BOM file updated with new components
- [ ] Dashboard loads and shows updated data
- [ ] GitHub repo has new commit
- [ ] Change summary looks correct
- [ ] No data loss (original files untouched)
- [ ] Dashboard URL works in browser

## 💡 Tips & Best Practices

### File Naming
Use consistent naming: `{Customer}_{Location}_{Version}.xlsx`
- IREN_Mackenzie.xlsx (good)
- IREN-Mackenzie.xlsx (adjust pattern in config)
- Mackenzie_IREN.xlsx (customize pattern)

### Deduplication Review
Always review matches during Step 4:
- Look for subtle differences in names/descriptions
- Check quantities make sense when summed
- Flag uncertain matches for manual investigation

### Backup Strategy
Skill creates automatic backups:
- Original master BOM saved before update
- Git history preserves all versions
- Can revert any change: `git revert <commit>`

### Scaling
This skill is designed for:
- Consolidating up to 100+ files
- Deduplicating 10,000+ components
- Daily or weekly updates
- Team collaboration via GitHub

## 🤝 Integration with Dashboard

After consolidation completes:
1. Dashboard regenerates automatically
2. Lives at GitHub Pages URL
3. Shows charts, tables, filters
4. Accessible to your team

Dashboard URL example:
```
https://abdullahabuzaid2021.github.io/L11-BOM-Agent/dashboard/
```

## ❓ FAQ

**Q: Can I consolidate the same files multiple times?**
A: Yes. Deduplication will recognize existing components and sum quantities.

**Q: What if I make a mistake during the wizard?**
A: You approve each step before proceeding. If you mess up, reject and start over.

**Q: Can I consolidate BOMs from different formats?**
A: The wizard expects Excel files. Other formats need to be converted first.

**Q: How long does consolidation take?**
A: Depends on file count and size. Typically:
- 5 files: ~2 minutes
- 19 files: ~5 minutes
- 100 files: ~15 minutes

**Q: What if GitHub push fails?**
A: All local updates succeed. Push can be retried manually later.

**Q: Can multiple people use the skill?**
A: Yes, via Git collaboration. Just coordinate who's consolidating.

## 📞 Support

- Review `SKILL.md` for detailed workflow documentation
- Check `references/bom_config.yaml` for all configuration options
- See `evals/evals.json` for example usage scenarios
- Review session logs for troubleshooting

---

**Version**: 1.0  
**Last Updated**: October 5, 2026  
**Status**: Production Ready  

**Questions?** Ask Claude to run the skill or review the detailed SKILL.md documentation.
