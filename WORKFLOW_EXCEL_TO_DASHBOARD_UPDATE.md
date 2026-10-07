# Workflow: Update BOM Excel & Dashboard from Devin Data

## 📋 Overview

This document defines the complete workflow for:
1. Receiving Focus ID data from Devin
2. Updating the reference BOM Excel file
3. Regenerating the dashboard with new data
4. Pushing updates to GitHub

---

## 🔄 Complete Workflow Steps

### **Phase 1: Receive Data from Devin**

**Input:** CSV file with Focus ID data (from Devin's extraction)

**Format Expected:**
```csv
Column,BOM File Name,Customer,Location,Focus ID,SFDC ID,Target Start Date,Target End Date
7,BOM - NETWORK - 2026-08-24- IREN...,IREN,Childress Tx,FOCUS-2657,31064701,2026-01-28,2026-11-01
...
```

**Validation Checklist:**
- [ ] All 18-19 BOM files present
- [ ] Focus IDs populated (or marked "NOT FOUND")
- [ ] SFDC IDs present (or marked "NOT FOUND")
- [ ] Target dates in YYYY-MM-DD format
- [ ] No empty cells except legitimate blanks

---

### **Phase 2: Update Excel File**

**Input File:** `BOM/BOM_FINAL.xlsx`

**Process:**

#### Step 1: Backup Original
```bash
cp BOM/BOM_FINAL.xlsx BOM/BOM_FINAL_BACKUP_$(date +%Y%m%d_%H%M%S).xlsx
```

#### Step 2: Parse Devin's CSV
Read the CSV file to extract:
- Column numbers (G-X = 7-24)
- Focus ID values
- SFDC ID values
- Target Start dates
- Target End dates

#### Step 3: Update Excel Rows 5-8
For each BOM file column:
- **Row 5:** Focus ID
- **Row 6:** SFDC ID
- **Row 7:** Target Start Date
- **Row 8:** Target End Date

#### Step 4: Update All Tabs
Apply the same updates to all 3 sheets:
1. Summary per sections
2. Summary Total
3. Summary total comparison

#### Step 5: Verify Data
- [ ] All 18-19 columns updated
- [ ] Rows 5-8 populated correctly
- [ ] No data corruption
- [ ] File opens without errors

**Python Script Example:**
```python
import pandas as pd
import openpyxl

# 1. Read mapping CSV from Devin
mapping_df = pd.read_csv('BOM_Metadata_Mapping_Template.csv')

# 2. Open Excel file
wb = openpyxl.load_workbook('BOM/BOM_FINAL.xlsx')

# 3. Create mapping dictionary
data_map = {}
for idx, row in mapping_df.iterrows():
    col = int(row['Column'])
    data_map[col] = {
        'Focus ID': row['Focus ID'] if row['Focus ID'] != 'NOT FOUND' else '',
        'SFDC ID': row['SFDC ID'] if row['SFDC ID'] != 'NOT FOUND' else '',
        'Target Start Date': row['Target Start Date'] if row['Target Start Date'] != 'NOT FOUND' else '',
        'Target End Date': row['Target End Date'] if row['Target End Date'] != 'NOT FOUND' else ''
    }

# 4. Update all sheets
for sheet_name in wb.sheetnames:
    ws = wb[sheet_name]
    for col, data in data_map.items():
        ws.cell(5, col).value = data['Focus ID']
        ws.cell(6, col).value = data['SFDC ID']
        ws.cell(7, col).value = data['Target Start Date']
        ws.cell(8, col).value = data['Target End Date']

# 5. Save
wb.save('BOM/BOM_FINAL.xlsx')
print("✅ Excel file updated successfully")
```

---

### **Phase 3: Regenerate Dashboard**

**Current Status:** Dashboard has EMBEDDED data (static JSON)

**Two Options:**

#### Option A: Manual Regeneration (Current)
1. Extract data from updated Excel
2. Update HTML with new data
3. Re-embed in dashboard HTML
4. Test and validate

**Command:**
```bash
# Run Python script to extract data from Excel and regenerate HTML
python3 scripts/regenerate_dashboard.py \
  --input BOM/BOM_FINAL.xlsx \
  --template dashboard-templates/BOM_Dashboard_TEMPLATE_v2.html \
  --output BOM_Dashboard_Final.html
```

#### Option B: Automatic Regeneration (Recommended for Future)
Create a script that:
1. Watches for changes to BOM_FINAL.xlsx
2. Automatically extracts data
3. Regenerates dashboard HTML
4. Pushes to GitHub automatically

**Script to Create:**
```python
# watch_and_regenerate.py
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class ExcelChangeHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if 'BOM_FINAL.xlsx' in event.src_path:
            print(f"📊 Excel file changed: {event.src_path}")
            regenerate_dashboard()
            push_to_github()

def regenerate_dashboard():
    # Extract from Excel → Update HTML → Save
    pass

def push_to_github():
    # Commit and push changes
    pass

if __name__ == "__main__":
    observer = Observer()
    observer.schedule(ExcelChangeHandler(), path='.', recursive=True)
    observer.start()
    try:
        while True:
            time.sleep(1)
    finally:
        observer.stop()
        observer.join()
```

---

### **Phase 4: GitHub Push**

**Files to Commit:**
```bash
git add BOM/BOM_FINAL.xlsx
git add BOM_CONSOLIDATED_FINAL_WITH_FOCUS_ID.xlsx
git add BOM_Dashboard_Final.html
git add docs/dashboard/index.html
```

**Commit Message Template:**
```
Update: BOM data with Focus IDs from Devin

Data Updated:
- Focus IDs: X/19 found
- SFDC IDs: Y/19 found
- Target Start Dates: All updated
- Target End Dates: All updated

Dashboard regenerated with new metadata
All 3 Excel sheets updated consistently
GitHub Pages updated automatically
```

**Push:**
```bash
git push origin main
```

---

## 🔄 Dashboard Auto-Refresh

### **Current Architecture (STATIC)**

**How it works:**
- Dashboard has EMBEDDED JSON data
- Data hardcoded in HTML
- Changes to Excel require HTML regeneration

**Pros:**
- ✅ Fast (no server needed)
- ✅ Works offline
- ✅ No dependencies
- ✅ Easy to deploy on GitHub Pages

**Cons:**
- ❌ Manual regeneration needed
- ❌ No auto-refresh
- ❌ Need to rebuild HTML for each update

---

### **Future Option 1: Dynamic Fetch (Client-Side)**

**How it would work:**
- Dashboard fetches data from Excel file via API
- Automatically updates when opened
- No manual regeneration needed

**Implementation:**
```javascript
// Fetch JSON data endpoint
fetch('/api/bom-data.json')
  .then(r => r.json())
  .then(data => {
    bomMetadata = data.components;
    bomFileNames = data.files;
    renderTables();
    renderCharts();
  });
```

**Requirements:**
- Server to serve API endpoint
- Excel → JSON conversion script
- API endpoint that reads latest Excel

**Pros:**
- ✅ Auto-refresh (always latest data)
- ✅ No HTML regeneration needed
- ✅ Dynamic updates

**Cons:**
- ❌ Requires backend server
- ❌ Won't work offline
- ❌ GitHub Pages limitation (static only)

---

### **Future Option 2: Build Pipeline (CI/CD)**

**How it would work:**
- GitHub Actions watches for Excel changes
- Automatically regenerates dashboard
- Commits and deploys on schedule

**GitHub Actions Workflow (.github/workflows/update-dashboard.yml):**
```yaml
name: Update BOM Dashboard

on:
  push:
    paths:
      - 'BOM/BOM_FINAL.xlsx'
  schedule:
    - cron: '0 12 * * *'  # Daily at noon

jobs:
  regenerate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Extract Excel Data
        run: python scripts/extract_bom_data.py
      
      - name: Regenerate Dashboard
        run: python scripts/regenerate_dashboard.py
      
      - name: Commit Changes
        run: |
          git add BOM_Dashboard_Final.html
          git commit -m "Auto: Dashboard regenerated from Excel"
          git push
```

**Pros:**
- ✅ Fully automated
- ✅ Works with GitHub
- ✅ No manual steps
- ✅ Scheduled updates possible

**Cons:**
- ⏱️ Slight delay (few minutes)
- 📝 Requires workflow setup

---

## 📊 Recommended Approach

### **Short-term (Now):**
✅ **Manual Workflow with Python Script**
- Devin provides CSV
- Python script updates Excel
- Python script regenerates HTML
- Push to GitHub

### **Medium-term (Next Sprint):**
⏳ **GitHub Actions CI/CD Pipeline**
- Automatically rebuild on Excel changes
- Scheduled daily regeneration
- Zero manual intervention

### **Long-term (Future):**
🚀 **Dynamic Dashboard with Backend**
- Real-time data fetching
- Auto-refresh capability
- Live metadata updates

---

## 🛠️ Scripts to Create

### Script 1: `update_excel_from_csv.py`
**Purpose:** Takes Devin's CSV and updates Excel

**Usage:**
```bash
python update_excel_from_csv.py \
  --csv BOM_Metadata_Mapping_Template.csv \
  --excel BOM/BOM_FINAL.xlsx
```

---

### Script 2: `regenerate_dashboard.py`
**Purpose:** Extracts Excel data and creates new HTML dashboard

**Usage:**
```bash
python regenerate_dashboard.py \
  --input BOM/BOM_FINAL.xlsx \
  --template dashboard-templates/BOM_Dashboard_TEMPLATE_v2.html \
  --output BOM_Dashboard_Final.html
```

---

### Script 3: `push_to_github.py`
**Purpose:** Automates git commit and push

**Usage:**
```bash
python push_to_github.py \
  --message "Update: BOM data with Focus IDs" \
  --files BOM_Dashboard_Final.html,BOM/BOM_FINAL.xlsx
```

---

## 📅 Workflow Timeline

```
Devin extracts Focus IDs
    ↓
Sends CSV file to you
    ↓
You run: update_excel_from_csv.py
    ↓
You run: regenerate_dashboard.py
    ↓
You run: push_to_github.py
    ↓
GitHub Pages auto-updates (5-30 seconds)
    ↓
Live dashboard shows new data
    ↓
Reference template updated with new version
```

**Total time:** ~5 minutes manual work

---

## ✅ Checklist for Each Update Cycle

**Receiving Data:**
- [ ] CSV received from Devin
- [ ] Validated: All 18-19 files present
- [ ] Validated: Required fields populated

**Updating Excel:**
- [ ] Backup created
- [ ] CSV parsed correctly
- [ ] Excel rows 5-8 updated
- [ ] All 3 sheets updated
- [ ] File validated (opens without errors)

**Regenerating Dashboard:**
- [ ] Data extracted from Excel
- [ ] HTML regenerated
- [ ] Charts render correctly
- [ ] Tables display properly
- [ ] Filters functional
- [ ] Export buttons working

**GitHub Push:**
- [ ] Files committed
- [ ] Commit message clear
- [ ] Push successful
- [ ] GitHub Pages updated
- [ ] Live dashboard verified

**Documentation:**
- [ ] Template updated (if major changes)
- [ ] README updated
- [ ] Version number incremented

---

## 🎯 Automation Goals

| Stage | Current | Phase 1 | Phase 2 | Phase 3 |
|-------|---------|---------|---------|---------|
| Data receipt | Manual | Manual | Manual | Auto |
| Excel update | Manual | Script | Script | Auto |
| Dashboard regen | Manual | Script | GitHub Actions | Auto |
| GitHub push | Manual | Script | Auto | Auto |
| Dashboard refresh | Manual | Manual | Auto (5-30s) | Real-time |
| Time per cycle | 30 min | 5 min | 1 min | 0 min |

---

## 📞 Need Help?

**For updating Excel:** Use `update_excel_from_csv.py`
**For regenerating dashboard:** Use `regenerate_dashboard.py`
**For pushing to GitHub:** Use `push_to_github.py`

All scripts include error handling and validation.

---

**Last Updated:** October 7, 2026
**Current Implementation:** Manual Script-based
**Next Target:** GitHub Actions CI/CD
**Future Vision:** Fully Automated with Real-time Updates
