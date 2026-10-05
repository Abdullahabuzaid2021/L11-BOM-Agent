# GitHub Pages Setup Guide

## 🚀 Host Your Dashboard on GitHub Pages

This guide walks you through publishing the BOM Dashboard to GitHub Pages for free, shareable hosting.

## Prerequisites
- GitHub account (free)
- Git installed on your computer (optional, but recommended)
- The dashboard files:
  - `BOM_Dashboard_Complete.html`
  - `BOM_CONSOLIDATED_FINAL_WITH_SECTIONS.xlsx`
  - `README_DASHBOARD.md`

## Step-by-Step Setup

### Step 1: Create `/docs` Folder in Your Repo

```bash
# In your local repo
mkdir -p docs/dashboard
```

### Step 2: Add Files to `/docs`

Copy these files to `docs/dashboard/`:
```
docs/
└── dashboard/
    ├── index.html  (rename BOM_Dashboard_Complete.html to index.html)
    ├── data.xlsx   (BOM_CONSOLIDATED_FINAL_WITH_SECTIONS.xlsx)
    └── README.md   (README_DASHBOARD.md)
```

### Step 3: Push to GitHub

```bash
git add docs/
git commit -m "Add BOM Dashboard - GitHub Pages hosting"
git push origin main
```

### Step 4: Enable GitHub Pages

1. Go to your repository: `https://github.com/Abdullahabuzaid2021/L11-BOM-Agent`
2. Click **Settings** (top menu)
3. Select **Pages** (left sidebar)
4. Under "Build and deployment":
   - **Source**: Select "Deploy from a branch"
   - **Branch**: Select "main"
   - **Folder**: Select "/ (root)" or "/docs" depending on your folder structure
5. Click **Save**

GitHub will automatically build your site (~1 minute).

### Step 5: Access Your Dashboard

After ~1-2 minutes, your dashboard is live at:

```
https://abdullahabuzaid2021.github.io/L11-BOM-Agent/dashboard/
```

## 📝 File Structure

```
L11-BOM-Agent/
├── docs/
│   └── dashboard/
│       ├── index.html                           (main dashboard)
│       ├── BOM_CONSOLIDATED_FINAL_WITH_SECTIONS.xlsx  (data file)
│       └── README_DASHBOARD.md                  (usage guide)
├── README.md                                    (main repo readme)
└── ... (other files)
```

## 🔄 Updating the Dashboard

When you update the dashboard:

1. Update `docs/dashboard/index.html` with new version
2. Update `docs/dashboard/BOM_CONSOLIDATED_FINAL_WITH_SECTIONS.xlsx` with new data
3. Commit and push:
   ```bash
   git add docs/dashboard/
   git commit -m "Update BOM Dashboard with latest data"
   git push origin main
   ```
4. Changes appear in ~30 seconds on GitHub Pages

## 🔗 Sharing the Dashboard

### Share the Link
Send this URL to your team:
```
https://abdullahabuzaid2021.github.io/L11-BOM-Agent/dashboard/
```

### In Email
```
Subject: BOM Dashboard - Network Infrastructure

Hi team,

I've published an interactive BOM dashboard with all 78 components.

View here: https://abdullahabuzaid2021.github.io/L11-BOM-Agent/dashboard/

Features:
- Real-time filtering by Customer, Location, Section
- Interactive charts and visualizations
- Export to CSV for analysis
- Works on desktop, tablet, mobile

Questions? See the README in the dashboard.

Best,
Abdullah
```

### In Slack
```
Check out the new BOM Dashboard! 📊

📍 Link: https://abdullahabuzaid2021.github.io/L11-BOM-Agent/dashboard/

Features:
• 78 network components
• 6 infrastructure sections
• Interactive visualizations
• CSV export capability

No installation needed - just open in your browser!
```

## 🛠️ Customization

### Change the Title
Edit the `<title>` tag in `index.html`:
```html
<title>BOM Dashboard - Your Company Name</title>
```

### Change the URL Path
Currently: `https://abdullahabuzaid2021.github.io/L11-BOM-Agent/dashboard/`

To use root: `https://abdullahabuzaid2021.github.io/L11-BOM-Agent/`
- Move `index.html` directly to `/docs`
- Update "Folder" setting in GitHub Pages to "/ (root)"

### Add Custom Domain
If your company has a domain:
1. In GitHub Pages settings, add your custom domain
2. Create a `CNAME` file in `/docs` with your domain name
3. Update DNS records (follow GitHub's instructions)

## 🔒 Privacy & Security

### This is Public
- GitHub Pages sites are publicly accessible
- Anyone with the URL can view the dashboard
- Data is embedded in HTML (not a database)

### If You Need Private Access
- Use GitHub Codespaces (paid)
- Host on private server
- Restrict with authentication (requires backend)

### Protect Sensitive Data
- Don't include passwords in the HTML
- Don't include API keys
- All data is visible in browser (view source)

## ❌ Troubleshooting

### Site Not Appearing
- **Check**: Build status in GitHub Pages settings
- **Wait**: GitHub takes 1-2 minutes to build
- **Try**: Hard refresh (Ctrl+Shift+R or Cmd+Shift+R)

### Old Version Still Showing
- **Clear**: Browser cache
- **Hard refresh**: Ctrl+Shift+R (Windows) or Cmd+Shift+R (Mac)
- **Wait**: CDN caching (usually 5 minutes max)

### 404 Error
- **Check**: File is in `/docs/dashboard/` folder
- **Verify**: Filename is exactly `index.html`
- **Confirm**: Repository is set to public

### Charts Not Loading
- **Check**: JavaScript is enabled
- **Verify**: HTML file is complete and valid
- **Try**: Different browser

## 📚 Next Steps

1. **Test the Dashboard**
   - Open it from the GitHub Pages URL
   - Try all filters and exports
   - Test on mobile device

2. **Share with Team**
   - Copy the URL above
   - Paste in Slack, email, or meeting
   - No special access needed

3. **Keep Updated**
   - Update BOM data in Excel
   - Regenerate dashboard HTML
   - Push to repo and GitHub Pages updates automatically

4. **Gather Feedback**
   - Ask team for suggestions
   - Track improvement requests
   - Update dashboard accordingly

## 📖 Resources

- [GitHub Pages Documentation](https://docs.github.com/en/pages)
- [GitHub Pages Custom Domain](https://docs.github.com/en/pages/configuring-a-custom-domain-for-your-github-pages-site)
- [Dashboard Usage Guide](README_DASHBOARD.md)
- [Data Update Instructions](DASHBOARD_DATA_UPDATE.md)

---

**Dashboard Live URL**: https://abdullahabuzaid2021.github.io/L11-BOM-Agent/dashboard/

**Questions?** Check the troubleshooting section or contact your GitHub admin.
