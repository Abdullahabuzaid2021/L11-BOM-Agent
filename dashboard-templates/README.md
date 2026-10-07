# BOM Dashboard Templates

## Templates Available

### BOM_Dashboard_TEMPLATE_v1.html
- **Date:** October 6, 2026
- **Status:** Previous version (deprecated)
- **Features:** Basic dashboard with 4 charts

### BOM_Dashboard_TEMPLATE_v2.html ⭐ CURRENT
- **Date:** October 7, 2026
- **Status:** Production-ready (Latest)
- **Version:** 2.0

## Features in v2.0

### Filters (6 combined filters)
- ✅ Customer filter (IREN, Anthropic, NScale)
- ✅ Location filter (12 locations, dynamic)
- ✅ Category filter (5 types)
- ✅ Section filter (6 sections)
- ✅ Quarter filter (Q1-Q4)
- ✅ Search filter (Model/PN, Description)
- ✅ Reset All Filters button

### Data Tables
- ✅ Summary per Sections (78 components)
- ✅ Summary Total (aggregated)
- ✅ Comparison (cross-view)
- ✅ All tables show 23 columns (Base + 18 Files + Total)
- ✅ Horizontal scrolling for wide tables
- ✅ Responsive design

### Charts (4 types)
- ✅ Category Distribution (Doughnut)
- ✅ Section/Customer Distribution (Bar)
- ✅ Component Quantities (Vertical bar - all 78 items)
- ✅ Real-time updates with filters

### Export Features
- ✅ CSV export for tables (all visible columns)
- ✅ PNG export for charts (high quality)
- ✅ Timestamped filenames
- ✅ Respects applied filters

### Metadata Integration
- ✅ Focus IDs (13/19 found)
- ✅ SFDC IDs (5/19 found)
- ✅ Target Start/End Dates
- ✅ Tab 4: Metadata & Files table

### Technical
- ✅ Self-contained HTML (no external dependencies except Chart.js CDN)
- ✅ All data embedded as JSON
- ✅ Mobile-responsive design
- ✅ Works offline (except CDN charts)
- ✅ 87 KB file size

## When to Use as Reference

Use `BOM_Dashboard_TEMPLATE_v2.html` when:
1. Creating new dashboard version
2. Rebuilding after corruption
3. Creating dashboard variations
4. Need working baseline with all features

## How to Use Template

1. Copy template file: `cp BOM_Dashboard_TEMPLATE_v2.html BOM_Dashboard_New.html`
2. Update data in embedded JSON objects
3. Test in browser
4. Deploy when ready

## File Locations

- **Current:** `/outputs/BOM_Dashboard_Final.html`
- **Template:** `/dashboard-templates/BOM_Dashboard_TEMPLATE_v2.html`
- **GitHub Pages:** `/docs/dashboard/index.html`
- **Data Source:** `/BOM/BOM_FINAL.xlsx`

---

**Last Updated:** October 7, 2026
**Recommended Version:** v2.0
**Status:** Production Ready ✅
