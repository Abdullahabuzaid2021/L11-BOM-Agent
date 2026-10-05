# Dashboard Data Update Guide

## 🔄 How to Update the BOM Dashboard

When your BOM data changes, follow this guide to update the dashboard and republish it.

## When to Update

Update the dashboard when:
- ✅ New BOM files are added
- ✅ Component quantities change
- ✅ New sections or categories created
- ✅ Customer/location information updates
- ✅ Data corrections needed

## Update Process (5 Steps)

### Step 1: Update Excel Data
```
1. Open: BOM_CONSOLIDATED_FINAL_WITH_SECTIONS.xlsx
2. Update relevant tabs:
   - Summary per sections
   - Summary Total
   - Summary total comparison
3. Save file
```

**Key fields to update:**
- Component quantities (file columns)
- Section assignments
- Category classifications
- Customer/location info

### Step 2: Generate New Dashboard HTML

Use this Python script to regenerate the dashboard:

```python
import openpyxl
import json

# Load the updated Excel file
wb = openpyxl.load_workbook('BOM_CONSOLIDATED_FINAL_WITH_SECTIONS.xlsx', data_only=True)

tabs_data = {}

for sheet_name in ['Summary per sections', 'Summary Total', 'Summary total comparison']:
    ws = wb[sheet_name]
    
    headers = [ws.cell(1, c).value for c in range(1, ws.max_column + 1)]
    customers = {headers[c-1]: ws.cell(2, c).value for c in range(1, len(headers) + 1)}
    locations = {headers[c-1]: ws.cell(3, c).value for c in range(1, len(headers) + 1)}
    
    items = []
    for row in range(5, ws.max_row + 1):
        pn = ws.cell(row, 1).value
        if pn:
            item = {}
            for col in range(1, len(headers) + 1):
                h = headers[col-1]
                v = ws.cell(row, col).value
                if h in ['Model/PN', 'Description', 'NVIDIA Generic Part number', 'Dell PN', 'Category', 'Section']:
                    item[h] = str(v) if v else ''
                else:
                    try:
                        item[h] = int(v) if (v and isinstance(v, (int, float))) else 0
                    except:
                        item[h] = 0
            items.append(item)
    
    tabs_data[sheet_name] = {
        'headers': headers,
        'customers': customers,
        'locations': locations,
        'items': items,
        'fileColumns': [h for h in headers[5:-1] if h != 'Section']
    }

print(f"✅ Loaded {len(tabs_data)} tabs with updated data")
```

### Step 3: Update the HTML File

The HTML file contains embedded JSON data. You have two options:

**Option A: Auto-regenerate (Recommended)**
- Contact your system admin to run the Python script
- Script extracts data from Excel and updates HTML
- Takes ~5 minutes

**Option B: Manual Update**
- Replace the JSON data in HTML with new data
- Advanced - only if you're familiar with JSON
- Takes ~20 minutes

### Step 4: Push to Repository

```bash
# Navigate to your repo
cd L11-BOM-Agent

# Stage files
git add docs/dashboard/index.html
git add docs/dashboard/BOM_CONSOLIDATED_FINAL_WITH_SECTIONS.xlsx

# Commit with message
git commit -m "Update BOM Dashboard - new data as of [DATE]"

# Push to GitHub
git push origin main
```

### Step 5: Verify on GitHub Pages

1. Wait 30-60 seconds for GitHub to rebuild
2. Visit: `https://abdullahabuzaid2021.github.io/L11-BOM-Agent/dashboard/`
3. Check that new data appears in charts and tables
4. Hard refresh if needed (Ctrl+Shift+R or Cmd+Shift+R)

## Troubleshooting Updates

### Charts Show Old Data
- **Clear cache**: Ctrl+Shift+R or Cmd+Shift+R
- **Wait**: GitHub caching can take up to 5 minutes
- **Check**: Commit actually pushed to main branch

### Numbers Don't Match Excel
- **Verify**: All tabs in Excel were updated
- **Check**: JSON data in HTML is valid
- **Ensure**: Excel formulas were recalculated

### Dashboard Won't Load
- **Check**: index.html file is valid HTML
- **Validate**: JSON data is properly formatted
- **Try**: Opening in different browser

## Sample Update Workflow

```
Example: Adding new cluster to Scale Out Networking

1. Open BOM_CONSOLIDATED_FINAL_WITH_SECTIONS.xlsx
2. Add new items to Summary Total tab
3. Add quantities to relevant file columns
4. Set Section = "Scale Out Networking"
5. Update Summary per sections tab
6. Save Excel file
7. Run Python script to regenerate HTML
8. git add, commit, push
9. Verify on GitHub Pages (30 seconds)
10. Share updated dashboard URL with team
```

## Advanced: Batch Updates

For multiple file updates:

```bash
# Update multiple files at once
git add docs/dashboard/*

# Single commit for all changes
git commit -m "Update dashboard: New BOMs for [Customer], [Date]"

# Push all at once
git push origin main
```

## Collaboration Tips

### Multiple Team Members

If multiple people update data:

```bash
# Always pull latest before editing
git pull origin main

# Edit your files
# ... (update Excel, regenerate HTML)

# Push your changes
git add .
git commit -m "Update BOM - [Your Name] - [Date]"
git push origin main
```

### Version Control

Track major updates:

```bash
# Tag important versions
git tag -a v1.1 -m "Dashboard update - Oct 2026"
git push origin v1.1
```

## Automating Updates (Advanced)

### GitHub Actions (Optional)

You can automate HTML regeneration:

1. Create `.github/workflows/update-dashboard.yml`
2. Trigger on Excel file changes
3. Auto-run Python script and commit

Requires GitHub Actions knowledge.

## When to Archive

Keep old data in git history:
```bash
# Create backup branch
git branch backup/bom-v1.0
git push origin backup/bom-v1.0

# Continue on main with new data
```

## Performance Notes

- Dashboard loads entire dataset in JSON
- File size increases with more data (~5KB per 10 items)
- Currently ~350KB for 78 items
- Acceptable for browser loading

If dataset grows significantly (1000+ items), consider:
- Splitting into smaller datasets
- Adding server-side filtering
- Using separate sheets per customer

## Questions?

See [README_DASHBOARD.md](README_DASHBOARD.md) for usage questions

See [GITHUB_PAGES_SETUP.md](GITHUB_PAGES_SETUP.md) for hosting questions

---

**Last Updated**: October 5, 2026
**Dashboard Version**: 1.0
