# BOM Dashboard - Network Infrastructure

## Overview
Complete Network Infrastructure Bill of Materials (BOM) Dashboard with interactive visualization of 78 components across 6 network sections and 19 source files.

**Live Dashboard**: [View Dashboard](https://abdullahabuzaid2021.github.io/L11-BOM-Agent/dashboard/)

## Features

### 📊 Interactive Visualizations
- **Category Distribution**: Doughnut chart showing component types
- **Customer Quantities**: Horizontal bar chart by customer
- **Location Quantities**: Horizontal bar chart by location  
- **Component Quantities**: Vertical bar chart per item with section color-coding

### 🔍 Advanced Filtering
- Filter by Customer, Category, Location, Section
- Real-time chart and table updates
- Works on all 3 data tabs

### 📋 Complete Data Table
- All 78 components with full details
- 19 file columns showing quantities per source
- Total quantity calculations
- Color-coded sections

### 📥 Export Functionality
- Export filtered results as CSV
- Timestamp included in filename
- Works with current filters

## Quick Start

### Option 1: View Online (Easiest)
1. Visit: https://abdullahabuzaid2021.github.io/L11-BOM-Agent/dashboard/
2. No installation required
3. Works in any modern browser

### Option 2: Local Viewing
1. Download `BOM_Dashboard_Complete.html`
2. Open in your web browser
3. Works offline once opened

## 📋 Data Structure

### 6 Network Sections
- **E-W Networking** (5.1%): SN4700, low-latency switches
- **OOB Networking** (7.7%): SN2201, management infrastructure
- **N-S Networking** (34.6%): SN5610/6800/6810 spines, high-speed
- **Scale Out Networking** (37.2%): Anthropic/NScale RoCE network
- **Racks, PDUs and CDUs** (9.0%): Infrastructure
- **Patch Panels / Shuffle** (6.4%): Panel infrastructure

### 19 Source Files
**IREN (9 files)**
- Mackenzie (512 Racks, B300)
- Childress (256 Racks, B300 & B200)
- Prince George (4x Test Racks)
- Sweetwater (252 Racks, NVL72) - 2 variants
- Horizon (210 Racks, NVL72) - 2 variants

**Anthropic (5 files)**
- Australia (Q1/Q2, 21k GPUs)
- Canada (Q2, 32k GPUs)
- US-Cluster1 (Q1/Q2, 129k GPUs)
- US-Cluster2 (Q1/Q2, 129k GPUs)
- US-Cluster3 (Q1/Q2, 9k GPUs)

**NScale/CTO (4 files)**
- Narvik 8k-6810
- Narvik 8k
- Narvik 17k
- US-TBD 18k

## 📊 Using the Dashboard

### Navigation
1. **Tabs**: Switch between "Summary per sections", "Summary Total", "Summary total comparison"
2. **Filters**: Use dropdowns to filter by Customer, Category, Location, Section
3. **Charts**: Hover over bars/segments for values
4. **Table**: Shows all filtered items with quantities

### Common Tasks

**Find items in a specific section:**
1. Go to "Summary per sections" tab
2. Select section from "Section" filter
3. View filtered results in table and charts

**Export component list for procurement:**
1. Apply desired filters (Customer, Location, etc.)
2. Click "📥 Export CSV"
3. Open in Excel for further processing

**See total quantities across all locations:**
1. Go to "Summary Total" tab
2. No filters applied = all items visible
3. Check "Total" column for sums

## 🔄 Updating the Dashboard

### When to Update
- New BOM files added to source data
- Categories or sections changed
- New component items discovered

### How to Update
1. Update `BOM_CONSOLIDATED_FINAL_WITH_SECTIONS.xlsx`
2. Run Python script: `python3 update_dashboard.py`
3. Upload updated `BOM_Dashboard_Complete.html`

[See Data Update Guide](DASHBOARD_DATA_UPDATE.md)

## 📁 Files Included

| File | Purpose |
|------|---------|
| `BOM_Dashboard_Complete.html` | Interactive dashboard (main file) |
| `BOM_CONSOLIDATED_FINAL_WITH_SECTIONS.xlsx` | Source BOM data |
| `README_DASHBOARD.md` | This file - Usage guide |
| `DASHBOARD_DATA_UPDATE.md` | How to update dashboard |
| `GITHUB_PAGES_SETUP.md` | GitHub Pages hosting guide |

## 🌐 GitHub Pages Hosting

### One-time Setup
1. Go to repo settings → Pages
2. Set source to "Deploy from a branch"
3. Select "main" branch, "/docs" folder
4. Save - GitHub will build your site

### Access the Live Dashboard
- URL: `https://abdullahabuzaid2021.github.io/L11-BOM-Agent/dashboard/`
- Updates automatically when you push changes

[Detailed Setup Guide](GITHUB_PAGES_SETUP.md)

## 👥 Sharing with Team

### Share the Dashboard Link
- **For everyone**: https://abdullahabuzaid2021.github.io/L11-BOM-Agent/dashboard/
- No authentication needed
- Works on desktop, tablet, mobile

### Share the Data File
- Include `BOM_CONSOLIDATED_FINAL_WITH_SECTIONS.xlsx`
- For detailed analysis or updates
- Open in Excel or LibreOffice

### Share Both
- Full package for complete transparency
- Team can verify data sources
- Enable collaboration on updates

## ⚙️ Technical Details

### Technology Stack
- **Frontend**: HTML5, Chart.js (visualization)
- **Data Format**: JSON (embedded in HTML)
- **Compatibility**: Chrome, Firefox, Safari, Edge (all modern versions)
- **Requirements**: None - runs in browser

### Browser Support
- ✅ Chrome/Edge (latest)
- ✅ Firefox (latest)
- ✅ Safari (latest)
- ✅ Mobile browsers
- ⚠️ Requires JavaScript enabled

### File Size
- HTML Dashboard: ~350KB
- Excel Data: ~40KB
- **Total**: ~390KB

## 📞 Support

### Common Issues

**Charts not showing?**
- Enable JavaScript in browser
- Try a different browser
- Clear browser cache

**Filters not working?**
- Refresh page (Ctrl+R or Cmd+R)
- Check browser console for errors
- Ensure JSON data is valid

**Export CSV is empty?**
- Apply filters to show items first
- Check that data is filtered correctly
- Try resetting filters

### Get Help
- Check [DASHBOARD_DATA_UPDATE.md](DASHBOARD_DATA_UPDATE.md)
- Review [GITHUB_PAGES_SETUP.md](GITHUB_PAGES_SETUP.md)
- Contact repository maintainer

## 📝 Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | Oct 2026 | Initial release - 78 items, 6 sections |
| | | Panel category merged under Rack |
| | | GitHub Pages hosting enabled |

## 📄 License
Internal use - Anthropic Network Infrastructure

---
**Last Updated**: October 5, 2026
**Maintainer**: Abdullah Abuzaid
**Repository**: https://github.com/Abdullahabuzaid2021/L11-BOM-Agent
