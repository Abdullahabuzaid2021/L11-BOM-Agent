# L11-BOM-Agent: BOM Consolidation Solution with Reference Management & Intake System

## 🎯 Overview

A comprehensive Bill of Materials (BOM) consolidation solution for Anthropic Network Infrastructure. Consolidates 78 network components from 19 source files (9 IREN, 5 Anthropic, 4-5 NScale/CTO) into a single master BOM with interactive dashboard visualization, section-based organization, and reusable Claude skills for automation.

**Status**: ✅ Production Ready | 78 Components | 6 Network Sections | 19 Source Files | Automated Skills Available

---

## 🚀 Quick Start

### 1. View the Dashboard
**Live Dashboard**: https://abdullahabuzaid2021.github.io/L11-BOM-Agent/dashboard/

Interactive dashboard with:
- 4 charts (category, customer, location, component quantities)
- Real-time filtering
- CSV export
- Mobile-friendly design

### 2. Use the BOM Consolidation Skill
**Interactive Setup** (Recommended):
```
Tell Claude: "I need to consolidate BOM files into a master inventory"

Claude will guide you through an interactive 6-step wizard:
1. File discovery
2. Metadata extraction
3. Section mapping
4. Deduplication
5. Aggregation review
6. Update & GitHub push
```

**Automated Setup** (For Daily Updates):
```bash
python skill/bom-consolidation-wizard/scripts/consolidate_bom.py --batch
```

---

## 📊 Interactive Dashboard

### 🌐 Live Dashboard
**View Now**: https://abdullahabuzaid2021.github.io/L11-BOM-Agent/dashboard/

**Features**:
- 📊 **4 Interactive Charts**: Category distribution, Customer quantities, Location quantities, Component quantities
- 🔍 **Real-time Filtering**: Filter by Customer, Category, Location, Section
- 📋 **Complete Data Table**: All 78 components with all source file columns
- 📥 **CSV Export**: Download filtered data with timestamp
- 📱 **Mobile-Friendly**: Responsive design for all devices
- 🎨 **Color-Coded Sections**: Visual identification by network domain

### Dashboard Structure
- **Summary per Sections** tab - 78 items organized by 6 network domains
- **Summary Total** tab - Complete consolidated inventory
- **Summary Total Comparison** tab - Changes from previous version

---

## 🔄 Automated Consolidation with Claude Skills

### 🎯 BOM Consolidation Wizard Skill

A reusable Claude skill for consolidating multiple BOM files.

**What It Does**:
- Discovers multiple BOM files from your workspace
- Extracts customer & location metadata from filenames
- Maps section information from source files
- Intelligently deduplicates components
- Aggregates quantities across all sources
- Updates master BOM Excel file
- Regenerates dashboard automatically
- Commits & pushes to GitHub

**Two Modes**:

| Mode | Use Case | Interaction |
|------|----------|-------------|
| **Interactive** | Learning, validation, manual review | User approves each step |
| **Batch** | Scheduled updates, CI/CD, daily automation | No user interaction, auto-approvals |

**Features**:
- ✅ Smart file detection (new vs. previously processed)
- ✅ Detailed change reports (CSV & JSON)
- ✅ GitHub integration with auto-commit
- ✅ Configurable section mapping (30+ rules included)
- ✅ Audit trail of all changes
- ✅ Backup & rollback capability

**Get Started**:
1. Read the skill documentation: `skill/bom-consolidation-wizard/README.md`
2. Customize config: `skill/bom-consolidation-wizard/references/bom_config.yaml`
3. Run interactively or set up batch mode

See [Skills Documentation](skill/README.md) for complete details.

---

## 📁 Repository Structure

```
L11-BOM-Agent/
├── docs/
│   └── dashboard/
│       ├── index.html                           (Interactive dashboard)
│       ├── BOM_CONSOLIDATED_FINAL_WITH_SECTIONS.xlsx  (Master data)
│       └── README.md                            (Dashboard usage)
├── skill/
│   └── bom-consolidation-wizard/
│       ├── SKILL.md                             (Skill definition)
│       ├── README.md                            (User guide)
│       ├── scripts/
│       │   └── consolidate_bom.py              (Core engine)
│       ├── references/
│       │   └── bom_config.yaml                 (Configuration)
│       └── evals/
│           └── evals.json                      (Test cases)
├── BOM_CONSOLIDATED_FINAL_WITH_SECTIONS.xlsx   (Master BOM)
├── BOM_Dashboard_Complete.html                 (Dashboard application)
├── README_DASHBOARD.md                         (Dashboard guide)
├── GITHUB_PAGES_SETUP.md                       (Hosting guide)
├── DASHBOARD_DATA_UPDATE.md                    (Data refresh guide)
└── README.md                                   (This file)
```

---

## 🏗️ BOM Structure

### 78 Network Components Across 6 Sections

| Section | Items | % | Key Components |
|---------|-------|---|-----------------|
| **Scale Out Networking** | 29 | 37.2% | Anthropic/NScale RoCE infrastructure |
| **N-S Networking** | 27 | 34.6% | SN5610/5600/6800/6810 spines, transceivers |
| **Racks, PDUs, CDUs** | 7 | 9.0% | IR5000/9048/9148/9149, power distribution |
| **OOB Networking** | 6 | 7.7% | SN2201 switches, management cables |
| **Patch Panels/Shuffle** | 5 | 6.4% | Fiber panels, cassettes, connectors |
| **E-W Networking** | 4 | 5.1% | SN4700 leaf switches, low-latency |

### 19 Source Files

**IREN (9 files)** - GPU cluster infrastructure
- Mackenzie, Childress, Prince George, Sweetwater (2), Horizon (2)

**Anthropic (5 files)** - Cloud-scale deployments
- Australia, Canada, US-Cluster1/2/3

**NScale/CTO (4 files)** - Custom deployments
- Narvik 8k-6810, 8k, 17k, US-TBD-18k

---

## 📊 Master BOM File

**Location**: `BOM_CONSOLIDATED_FINAL_WITH_SECTIONS.xlsx`

### Structure (3 Tabs)
1. **Summary per sections** - 78 items organized by network section
2. **Summary Total** - Complete consolidated inventory
3. **Summary total comparison** - Cross-reference view

### Columns (24 Total)
- **Info (5)**: Model/PN, Description, NVIDIA PN, Dell PN, Category
- **Sections (1)**: Network section assignment
- **Files (18)**: Source file quantities
- **Totals (1)**: Sum across all files

### Categories (6)
- Switch, Transceiver, Cables, Panel, Rack, Other

---

## 🔄 Updating the Dashboard & Master BOM

### Method 1: Using the Claude Skill (Recommended)
```
Tell Claude: "I need to consolidate new BOM files"

Claude guides you through the entire workflow interactively.
```

### Method 2: Batch Automation
```bash
# Setup (one time)
cp skill/bom-consolidation-wizard/references/bom_config.yaml ./
# Edit config with your file paths

# Run
python skill/bom-consolidation-wizard/scripts/consolidate_bom.py --batch

# Result: Master BOM updated, dashboard regenerated, GitHub pushed
```

### Method 3: Manual Update
See [DASHBOARD_DATA_UPDATE.md](DASHBOARD_DATA_UPDATE.md) for manual refresh instructions.

---

## 📖 Documentation

### For End Users
- **[Dashboard Usage Guide](README_DASHBOARD.md)** - How to use filters, charts, export
- **[Dashboard Quick Start](docs/dashboard/README.md)** - Features overview and common tasks

### For Administrators
- **[GitHub Pages Setup](GITHUB_PAGES_SETUP.md)** - How to host and customize
- **[Data Update Guide](DASHBOARD_DATA_UPDATE.md)** - How to refresh data
- **[Skills Documentation](skill/README.md)** - How to use Claude skills for automation

### For Developers
- **[Skill Implementation](skill/bom-consolidation-wizard/SKILL.md)** - Complete skill definition
- **[Skill Code](skill/bom-consolidation-wizard/scripts/consolidate_bom.py)** - Core engine
- **[Data Structure](BOM_CONSOLIDATED_FINAL_WITH_SECTIONS.xlsx)** - Excel file with all data
- **[Dashboard Code](BOM_Dashboard_Complete.html)** - Single-file HTML5 application

---

## 🛠️ Technical Stack

### Frontend
- **HTML5** - Modern web standards
- **Chart.js** - Interactive data visualization
- **JavaScript** - Client-side filtering and interactions
- **CSS3** - Responsive design

### Backend / Automation
- **Python** - Data processing and orchestration
- **openpyxl** - Excel file manipulation
- **PyYAML** - Configuration management
- **Git CLI** - Version control integration

### Hosting
- **GitHub Pages** - Free, automatic hosting
- **Git** - Version control and collaboration

---

## 📤 Sharing with Team

### Share the Dashboard Link
```
https://abdullahabuzaid2021.github.io/L11-BOM-Agent/dashboard/
```

### Via Email
See [GITHUB_PAGES_SETUP.md - Sharing](GITHUB_PAGES_SETUP.md#-sharing-the-dashboard) for email template

### Via Slack
See [GITHUB_PAGES_SETUP.md - Sharing](GITHUB_PAGES_SETUP.md#in-slack) for Slack message template

---

## 🎯 Key Features

### Dashboard
- 📊 **4 Interactive Charts** - Visualize data by category, customer, location, component
- 🔍 **Multi-dimensional Filtering** - Real-time updates
- 📋 **Complete Data Table** - All 78 components with source details
- 📥 **CSV Export** - Download for analysis
- 📱 **Responsive Design** - Works on desktop, tablet, mobile

### Master BOM
- ✅ 78 unique components
- ✅ Organized by 6 network sections
- ✅ 19 source files tracked
- ✅ Complete metadata (Model/PN, Description, NVIDIA PN, Dell PN)
- ✅ Category classification
- ✅ Total quantities per component

### Automation (Skills)
- ✅ **Interactive Consolidation** - Step-by-step guidance
- ✅ **Batch Mode** - Scheduled/automated updates
- ✅ **Smart File Detection** - Skip already-processed files
- ✅ **Deduplication** - Intelligent matching algorithm
- ✅ **Change Reports** - CSV & JSON documentation
- ✅ **GitHub Integration** - Auto-commit with audit trail

---

## 🚀 Getting Started

### Option 1: View Online (Recommended)
1. Visit: https://abdullahabuzaid2021.github.io/L11-BOM-Agent/dashboard/
2. No setup required
3. Use filters and export as needed

### Option 2: Local Setup with Skill
1. Clone this repository
2. Install Claude skill: `skill/bom-consolidation-wizard.skill`
3. Use with Claude for interactive consolidations
4. Or run batch mode: `python skill/bom-consolidation-wizard/scripts/consolidate_bom.py --batch`

### Option 3: Manual Setup
1. Download `BOM_CONSOLIDATED_FINAL_WITH_SECTIONS.xlsx`
2. Download `BOM_Dashboard_Complete.html`
3. Open HTML file in your browser
4. Works offline

---

## ⚙️ System Requirements

### Browser
- Chrome/Edge (latest)
- Firefox (latest)
- Safari (latest)
- Mobile browsers (iOS Safari, Android Chrome)

### For Automation (Optional)
- Python 3.7+
- openpyxl, pyyaml libraries
- Git (for auto-commit feature)

---

## 🔒 Privacy & Security

### Data Handling
- All dashboard data embedded in HTML file
- No external API calls
- No data transmission to servers
- Works fully offline

### GitHub Pages
- Public repository (data is visible)
- No authentication required
- HTTPS enabled by default
- All data is viewable in browser

---

## 📞 Support

### Common Issues
- **Charts not showing?** → Enable JavaScript
- **Old data displayed?** → Clear browser cache (Ctrl+Shift+R)
- **Mobile issues?** → Try landscape mode
- **Skill not working?** → Check config file paths

### Getting Help
1. Check [Dashboard Usage Guide](README_DASHBOARD.md)
2. Review [Skill Documentation](skill/bom-consolidation-wizard/README.md)
3. See [GitHub Pages Setup](GITHUB_PAGES_SETUP.md) for hosting
4. Contact repository maintainer

---

## 📝 Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.1 | Oct 2026 | Added BOM Consolidation Wizard skill |
| | | New features: batch mode, smart file detection, change reports |
| | | Interactive consolidation with GitHub integration |
| 1.0 | Oct 2026 | Initial release |
| | | 78 components, 6 sections |
| | | GitHub Pages hosting |
| | | Interactive dashboard |

---

## 👥 Contributors

- **Abdullah Abuzaid** - Lead developer
- **Anthropic Network Team** - Requirements & data
- **Claude AI** - Tool development & skills

---

## 📄 License

Internal use - Anthropic Network Infrastructure

---

## 🎯 Quick Links

| What | Link |
|------|------|
| 🌐 Live Dashboard | https://abdullahabuzaid2021.github.io/L11-BOM-Agent/dashboard/ |
| 🔄 BOM Consolidation Skill | `skill/bom-consolidation-wizard/` |
| 📖 Skills Documentation | [skill/README.md](skill/README.md) |
| 📊 Dashboard Usage | [README_DASHBOARD.md](README_DASHBOARD.md) |
| 🛠️ Setup Guide | [GITHUB_PAGES_SETUP.md](GITHUB_PAGES_SETUP.md) |
| 🔄 Data Update Guide | [DASHBOARD_DATA_UPDATE.md](DASHBOARD_DATA_UPDATE.md) |
| 📊 Master BOM | [BOM_CONSOLIDATED_FINAL_WITH_SECTIONS.xlsx](BOM_CONSOLIDATED_FINAL_WITH_SECTIONS.xlsx) |

---

**Last Updated**: October 5, 2026  
**Dashboard Status**: ✅ Production Ready  
**Skill Status**: ✅ Production Ready  
**Components**: 78  
**Sections**: 6  
**Source Files**: 19  

**Questions?** See [skill/README.md](skill/README.md) for automation help or [README_DASHBOARD.md](README_DASHBOARD.md) for dashboard help.
