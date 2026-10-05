# Deployment Guide: Adding BOM Consolidation Skill to L11-BOM-Agent

This guide explains how to update your GitHub repository with the new BOM Consolidation Wizard skill and updated documentation.

## 📋 What's Being Added

1. **`/skill` folder** - New directory for Claude skills
2. **`/skill/bom-consolidation-wizard/`** - Complete BOM consolidation skill
   - `SKILL.md` - Skill definition
   - `README.md` - User guide
   - `scripts/consolidate_bom.py` - Core engine
   - `references/bom_config.yaml` - Configuration template
   - `evals/evals.json` - Test cases
3. **`skill/README.md`** - Skills folder documentation
4. **Updated `README.md`** - Main repository readme highlighting the skill

## 🚀 Deployment Steps

### Step 1: Clone Your Repository

```bash
cd ~
git clone https://github.com/Abdullahabuzaid2021/L11-BOM-Agent.git
cd L11-BOM-Agent
```

### Step 2: Create the `/skill` Directory Structure

```bash
# Create the skill folder structure
mkdir -p skill/bom-consolidation-wizard/{scripts,references,evals}
```

### Step 3: Add Skill Files

Copy the skill files to the repository. You have the files in:
- `bom-consolidation-wizard/SKILL.md` → `skill/bom-consolidation-wizard/SKILL.md`
- `bom-consolidation-wizard/README.md` → `skill/bom-consolidation-wizard/README.md`
- `bom-consolidation-wizard/scripts/consolidate_bom.py` → `skill/bom-consolidation-wizard/scripts/consolidate_bom.py`
- `bom-consolidation-wizard/references/bom_config.yaml` → `skill/bom-consolidation-wizard/references/bom_config.yaml`
- `bom-consolidation-wizard/evals/evals.json` → `skill/bom-consolidation-wizard/evals/evals.json`

**Quick copy command:**
```bash
cp -r /path/to/bom-consolidation-wizard/* skill/bom-consolidation-wizard/
```

### Step 4: Add Skills README

Place the `skill/README.md` file in the skill directory:

```bash
cp /path/to/skill-README.md skill/README.md
```

### Step 5: Update Main README

Replace the main `README.md` with the updated version:

```bash
# Backup the old one first
cp README.md README.md.backup

# Use the new version
cp /path/to/updated-README.md README.md
```

### Step 6: Verify the Structure

Check that your repository now looks like this:

```bash
tree -L 3 skill/

skill/
├── README.md
└── bom-consolidation-wizard/
    ├── SKILL.md
    ├── README.md
    ├── scripts/
    │   └── consolidate_bom.py
    ├── references/
    │   └── bom_config.yaml
    └── evals/
        └── evals.json
```

### Step 7: Stage Changes

```bash
# Add all new/modified files
git add skill/
git add README.md

# Check what will be committed
git status
```

### Step 8: Create Meaningful Commit

```bash
git commit -m "Add BOM Consolidation Wizard skill with batch mode & change reports

- Interactive wizard for consolidating multiple BOM files
- Batch mode for automated/scheduled consolidations  
- Smart file detection (new vs. previously processed files)
- Detailed change reports (CSV & JSON formats)
- GitHub integration with auto-commit
- Configuration template with 30+ section mappings
- Test cases and user documentation

Closes #[issue-number] (if applicable)"
```

### Step 9: Push to GitHub

```bash
git push origin main
```

Or if you prefer a separate branch first (safer):

```bash
# Create a new branch
git checkout -b add/bom-consolidation-skill

# Push the branch
git push origin add/bom-consolidation-skill

# Then create a Pull Request on GitHub and review before merging
```

### Step 10: Verify on GitHub

1. Go to https://github.com/Abdullahabuzaid2021/L11-BOM-Agent
2. Check that the `/skill` folder is visible
3. Verify the updated `README.md` shows the skill documentation
4. Review the skill files are all present

## ✅ Verification Checklist

After pushing, verify everything is working:

- [ ] `/skill` folder exists in repository
- [ ] `skill/README.md` is present and readable
- [ ] `skill/bom-consolidation-wizard/` folder exists
- [ ] All skill files present:
  - [ ] `SKILL.md`
  - [ ] `README.md`
  - [ ] `scripts/consolidate_bom.py`
  - [ ] `references/bom_config.yaml`
  - [ ] `evals/evals.json`
- [ ] Main `README.md` updated with skill section
- [ ] Skills section has links to skill documentation
- [ ] Dashboard link still works
- [ ] All other documentation files still accessible

## 🎯 Next Steps After Deployment

### 1. Make Skill Available to Claude

The skill is now in your repository. To use it with Claude:

**Option A: Save as installed skill**
```bash
# Create a .skill file (zipped package)
cd skill
zip -r bom-consolidation-wizard.skill bom-consolidation-wizard/
# Download and click "Save skill" in Claude to install
```

**Option B: Use directly from repository**
- Clone your repository
- Reference the skill path when using with Claude
- Or copy to your Claude configuration directory

### 2. Configure for Your Environment

Users need to customize the configuration:

```bash
# Copy the config template
cp skill/bom-consolidation-wizard/references/bom_config.yaml ./bom_config.yaml

# Edit for your setup:
# - File paths
# - Column mappings
# - Section names
# - GitHub repo path
```

### 3. Test the Skill

**Interactive test:**
```bash
# Tell Claude to use the skill
"I need to consolidate my BOM files"

# Claude will guide you through the workflow
```

**Batch test:**
```bash
# Configure bom_config.yaml first, then:
python skill/bom-consolidation-wizard/scripts/consolidate_bom.py --batch
```

### 4. Set Up Automation (Optional)

Schedule daily consolidations:

```bash
# Create a cron job (daily at 2am)
0 2 * * * cd /path/to/L11-BOM-Agent && python skill/bom-consolidation-wizard/scripts/consolidate_bom.py --batch >> logs/bom.log 2>&1
```

Or use GitHub Actions for serverless automation.

## 🔄 Updating the Skill in the Future

When you improve the skill:

```bash
# Edit the skill files
nano skill/bom-consolidation-wizard/scripts/consolidate_bom.py

# Test locally
python skill/bom-consolidation-wizard/scripts/consolidate_bom.py --batch

# Commit & push
git add skill/
git commit -m "Improve: [describe improvements]"
git push origin main
```

## 📚 Documentation Hierarchy

After deployment, users will find:

1. **Main README** (`README.md`) - Overview and quick start
2. **Skills README** (`skill/README.md`) - All available skills
3. **Skill-Specific README** (`skill/bom-consolidation-wizard/README.md`) - How to use this skill
4. **Skill Definition** (`skill/bom-consolidation-wizard/SKILL.md`) - Complete workflow details
5. **Configuration** (`skill/bom-consolidation-wizard/references/bom_config.yaml`) - Customization

Users can navigate: Main README → Skills README → Specific Skill Documentation

## 🆘 Troubleshooting Deployment

### Issue: Files not showing in GitHub

**Solution:**
```bash
# Make sure you've committed and pushed
git status  # Should show "nothing to commit"

# Verify with:
git log --oneline -5
```

### Issue: Large file error

If Python script is too large:
```bash
# GitHub has 100MB file limit, but .py files are usually small
# If you hit this, consider splitting the script
```

### Issue: Permission errors on Linux/Mac

```bash
# Make Python script executable
chmod +x skill/bom-consolidation-wizard/scripts/consolidate_bom.py

# Then re-add
git add skill/
git commit --amend --no-edit
```

## 📞 Support

If you encounter issues:

1. **Check the deployment checklist above** - Often just a missing step
2. **Verify file paths** - Make sure files are in the right locations
3. **Review git status** - `git status` shows what's tracked
4. **Check repository online** - Verify files actually pushed to GitHub

## 🎉 Success!

Once deployed, your repository will have:

- ✅ Complete BOM consolidation skill ready to use
- ✅ Documentation for end users and developers
- ✅ Automated consolidation capability
- ✅ Test cases for validation
- ✅ Configuration template for customization
- ✅ Updated main README highlighting the solution

Users can now:
- Use the skill interactively with Claude
- Set up automated daily consolidations
- Generate detailed change reports
- Maintain audit trails in Git
- Share the dashboard with their team

---

**Deployment Date**: October 5, 2026  
**Repository**: https://github.com/Abdullahabuzaid2021/L11-BOM-Agent  
**Skill Version**: 1.0  

**Next**: Configure the skill for your environment and test with real BOM files!
