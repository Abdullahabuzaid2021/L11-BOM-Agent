# GitHub Actions CI/CD Setup - Auto Dashboard Updates

## 🚀 Overview

This setup enables **automatic dashboard regeneration** when the Excel file changes or on a daily schedule.

**Benefits:**
- ✅ Zero manual intervention needed
- ✅ Dashboard always up-to-date
- ✅ Automatic GitHub Pages deployment
- ✅ Scheduled daily regeneration
- ✅ Triggered on Excel changes

---

## 📋 Files to Add to Repository

### 1. **GitHub Actions Workflow** (Required)
**Path:** `.github/workflows/update-dashboard.yml`

This file tells GitHub Actions what to do when triggered.

**Key Features:**
- Triggers on: Excel file changes, manual dispatch, daily schedule
- Steps: Extract data → Regenerate dashboard → Commit → Push
- Runs on: Ubuntu-latest
- Time: ~2-3 minutes per run

### 2. **Python Script: Extract Data**
**Path:** `scripts/extract_bom_data.py`

Extracts all data from Excel file and saves as JSON.

**Usage:**
```bash
python scripts/extract_bom_data.py BOM/BOM_FINAL.xlsx bom_data.json
```

### 3. **Python Script: Regenerate Dashboard**
**Path:** `scripts/regenerate_dashboard.py`

Creates new dashboard HTML from template and data.

**Usage:**
```bash
python scripts/regenerate_dashboard.py \
  --input BOM/BOM_FINAL.xlsx \
  --template dashboard-templates/BOM_Dashboard_TEMPLATE_v2.html \
  --output BOM_Dashboard_Final.html
```

---

## 🔧 Setup Instructions

### Step 1: Create Directory Structure

```bash
# In your L11-BOM-Agent repository root
mkdir -p .github/workflows
mkdir -p scripts
```

### Step 2: Add the Workflow File

Copy `.github/workflows/update-dashboard.yml` to your repo.

This tells GitHub to:
- Watch for changes to `BOM/BOM_FINAL.xlsx`
- Run daily at 12:00 UTC
- Allow manual trigger via GitHub Actions tab

### Step 3: Add Python Scripts

Copy `scripts/extract_bom_data.py` and `scripts/regenerate_dashboard.py` to your repo.

### Step 4: Commit and Push

```bash
git add .github/workflows/update-dashboard.yml
git add scripts/extract_bom_data.py
git add scripts/regenerate_dashboard.py
git commit -m "Setup: GitHub Actions for auto dashboard updates"
git push origin main
```

### Step 5: Verify Setup

1. Go to your GitHub repo: https://github.com/Abdullahabuzaid2021/L11-BOM-Agent
2. Click **Actions** tab
3. Should see workflow: **🔄 Auto-Update BOM Dashboard**
4. Workflow should show as ready to run

---

## ⚙️ How It Works

### **Trigger 1: Excel File Changes**
```
You push changes to BOM/BOM_FINAL.xlsx
    ↓
GitHub detects change
    ↓
Triggers workflow automatically
    ↓
Extracts new data
    ↓
Regenerates dashboard
    ↓
Commits and pushes updates
    ↓
Dashboard live in 1-5 minutes
```

### **Trigger 2: Daily Schedule**
```
Every day at 12:00 UTC
    ↓
Workflow runs automatically
    ↓
Checks for updates
    ↓
Regenerates if changes found
    ↓
Commits if needed
```

### **Trigger 3: Manual**
```
Go to Actions tab
    ↓
Click "Run workflow"
    ↓
Manually trigger regeneration
    ↓
Useful for testing
```

---

## 🔄 Updated Workflow With Automation

### **Before (Manual - 5 minutes):**
```
Devin sends data
    ↓
You update Excel manually
    ↓
You run Python script (regenerate)
    ↓
You run git push manually
    ↓
Dashboard updates
```

### **After (Automated - 1-5 minutes):**
```
Devin sends data
    ↓
You update Excel (just save!)
    ↓
GitHub Actions auto-triggers
    ↓
Extracts → Regenerates → Pushes (automatic!)
    ↓
Dashboard updates automatically
```

---

## 📊 Workflow Execution

### **What Happens Each Run:**

1. **Checkout Code** (10 seconds)
   - Gets latest repo code

2. **Setup Python** (15 seconds)
   - Installs Python 3.10

3. **Install Dependencies** (30 seconds)
   - pip install openpyxl pandas

4. **Extract Data** (20 seconds)
   - Reads Excel file
   - Generates JSON

5. **Check Changes** (5 seconds)
   - Detects if data changed

6. **Regenerate Dashboard** (30 seconds)
   - Creates new HTML
   - Updates GitHub Pages copy

7. **Commit & Push** (20 seconds)
   - Auto-commits changes
   - Pushes to main branch

8. **GitHub Pages** (30-60 seconds)
   - Auto-deploys to GitHub Pages
   - Dashboard goes live

**Total Time:** ~2-3 minutes

---

## 🔍 Monitoring Workflow Runs

### **View Workflow Status:**

1. Go to: https://github.com/Abdullahabuzaid2021/L11-BOM-Agent/actions
2. Click **🔄 Auto-Update BOM Dashboard** workflow
3. See all runs with status (✅ success or ❌ failure)

### **View Run Details:**

1. Click on a run
2. See each step with timing
3. View logs for any step
4. See commit message created

### **Check Dashboard Update:**

1. Go to: https://abdullahabuzaid2021.github.io/L11-BOM-Agent/dashboard/
2. Refresh (Ctrl+Shift+R for hard refresh)
3. Should see latest data within 1-5 minutes of trigger

---

## 🛠️ Troubleshooting

### **Workflow Doesn't Trigger**

**Check:**
- [ ] Workflow file is in `.github/workflows/` folder
- [ ] File name is `update-dashboard.yml`
- [ ] Pushed to main branch
- [ ] No syntax errors in YAML

**Fix:**
```bash
# Re-push workflow
git add .github/workflows/update-dashboard.yml
git commit -m "Fix: Workflow configuration"
git push origin main
```

---

### **Workflow Runs But Fails**

**Check logs:**
1. Go to Actions tab
2. Click failed run
3. Click job to see error
4. Common issues:
   - Missing Python dependencies
   - Excel file path incorrect
   - Template file not found

**Fix:**
```bash
# Update scripts and re-push
git add scripts/
git commit -m "Fix: Script errors"
git push origin main
```

---

### **Dashboard Doesn't Update**

**Check:**
1. Workflow runs successfully (check Actions tab)
2. Dashboard commit created (check git log)
3. GitHub Pages deployed (wait 1-5 minutes)
4. Hard refresh dashboard (Ctrl+Shift+R)

**Common causes:**
- Browser cache (hard refresh)
- Network delay (wait 5 minutes)
- GitHub Pages deployment delay

---

## 📈 Workflow Statistics

| Metric | Value |
|--------|-------|
| **Execution Time** | 2-3 minutes |
| **Trigger on Excel change** | Automatic |
| **Daily schedule** | 12:00 UTC |
| **Manual trigger** | Available |
| **GitHub Pages deploy** | 1-5 minutes |
| **Logs retention** | 90 days |
| **Cost** | Free (GitHub Actions) |

---

## 🎯 Next Steps After Setup

### **When Devin Provides New Data:**

1. Update Excel file with new Focus IDs
2. Push to GitHub
3. **Done!** Workflow handles the rest

```bash
# Update Excel with Devin's data
# Then just:
git add BOM/BOM_FINAL.xlsx
git commit -m "Update: New Focus IDs from Devin"
git push origin main

# Workflow automatically:
# ✅ Extracts data
# ✅ Regenerates dashboard
# ✅ Updates GitHub Pages
# ✅ Creates commit with details
```

---

## 📝 Maintenance

### **Monthly Tasks:**

- [ ] Check workflow runs in Actions tab
- [ ] Verify dashboard updates working
- [ ] Review any failed runs
- [ ] Update scripts if needed

### **When Something Breaks:**

1. Check Actions tab for error logs
2. Review recent changes to Excel/scripts
3. Check GitHub Issues for help
4. Re-push workflow file if needed

---

## 🚀 Scaling for Multiple Updates

### **If Devin Sends Multiple Updates Per Day:**

```bash
# Current: Runs daily + on Excel changes
# Result: Dashboard updates within 5 minutes of each Excel change
```

This setup handles multiple daily updates automatically!

---

## 🎓 Learning Resources

**GitHub Actions Documentation:**
- https://docs.github.com/en/actions/quickstart

**Workflow Syntax:**
- https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions

**Python in Actions:**
- https://docs.github.com/en/actions/automating-builds-and-testing/building-and-testing-python

---

## ✅ Completion Checklist

- [ ] `.github/workflows/update-dashboard.yml` added to repo
- [ ] `scripts/extract_bom_data.py` added to repo
- [ ] `scripts/regenerate_dashboard.py` added to repo
- [ ] Files committed and pushed to main
- [ ] Workflow appears in Actions tab
- [ ] Can see "🔄 Auto-Update BOM Dashboard" workflow
- [ ] Tested manual trigger (optional but recommended)
- [ ] Dashboard updates when Excel changes

---

**Status:** ✅ Ready for Production

**Version:** 1.0

**Last Updated:** October 7, 2026

**Next Target:** Full data-driven dashboard with real-time updates
