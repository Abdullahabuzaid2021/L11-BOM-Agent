# BOM Dashboard Reference Template

This directory contains the reference template for BOM dashboards.

## Overview

`BOM_Dashboard_TEMPLATE_v1.html` is the baseline template that includes all features for a complete BOM (Bill of Materials) dashboard. Use this as the foundation when rebuilding or modifying the dashboard.

## Features Included

- **Target End Date Quarter filter (Q1-Q4)** - Filter components by fiscal quarter
- **Count by Items chart** - Shows actual quantities per component
- **4 Main Charts:**
  - Category Distribution - Visual breakdown by product categories
  - Section Distribution - Breakdown by document sections
  - Component Quantities - Detailed quantities for each component
  - Metadata - File and data information
- **4 Interactive Tabs:**
  - Summary per Sections - View metrics aggregated by section
  - Summary Total - Overall consolidated summary
  - Comparison - Compare across different dimensions
  - Metadata & Files - File sources and metadata details
- **Real-time Filtering** - Dynamic chart updates as filters are applied
- **All 19 BOM Files** - Complete integration with all source BOMs
- **Responsive Design** - Works across different screen sizes
- **Professional Styling** - Clean, modern UI with proper visual hierarchy

## When to Use This Template

Use this template as your baseline when:

- Rebuilding the BOM dashboard from scratch
- Adding new features to the dashboard
- Modifying existing filtering logic
- Updating chart visualizations
- Refreshing dashboard styling
- Creating variants for different stakeholders

## Modification Instructions

1. **To Add New Data Sources:**
   - Locate the data loading section at the top of the HTML file
   - Add references to new BOM files in the data array
   - Update metadata extraction to include new file information

2. **To Modify Charts:**
   - Find the chart initialization code
   - Update the chart configuration, data bindings, and series settings
   - Test chart rendering and interactivity

3. **To Change Filters:**
   - Locate the filter element definitions
   - Modify filter options, labels, and binding logic
   - Update the filtering functions that apply to charts

4. **To Update Styling:**
   - Locate the CSS section in the `<style>` tag
   - Modify colors, fonts, spacing, and layouts
   - Test responsive behavior across screen sizes

5. **To Extend Tabs:**
   - Add new tab definitions in the tab container
   - Create corresponding tab content sections
   - Bind data and interactivity to new tabs

## Technical Details

- **Format:** Single-file HTML5 application
- **Dependencies:** Built-in JavaScript (no external CDN required for core functionality)
- **Data Format:** JSON-compatible internal data structures
- **Browser Support:** Modern browsers with ES6 support

## Support and Maintenance

For questions or issues with this template:
- Review the original implementation for reference
- Check the Features list above for complete capabilities
- Ensure all 19 BOM files are properly referenced
- Validate that all four tabs render correctly
- Test all filter combinations before deployment

---

**Version:** 1.0  
**Last Updated:** 2026-10-07  
**Maintained by:** BOM Dashboard Development Team
