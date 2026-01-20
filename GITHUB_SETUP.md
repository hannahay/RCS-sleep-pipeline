# GitHub Repository Setup

This repository is ready to be pushed to GitHub. Follow these steps:

## 1. Create GitHub Repository

1. Go to https://github.com/new
2. Repository name: `RCS-sleep-pipeline` (or `RCS-SC-pipeline` if you prefer)
3. Description: "Pipeline for analyzing sleep data from Responsive Cortical Stimulation (RCS) devices"
4. Choose visibility (Public or Private)
5. **Do NOT** initialize with README, .gitignore, or license (we already have these)
6. Click "Create repository"

## 2. Push to GitHub

After creating the repository, GitHub will show you commands. Use these:

```bash
cd /home/hannac/Documents/RCS-sleep-pipeline

# Add the remote (replace YOUR_USERNAME with your GitHub username)
git remote add origin https://github.com/YOUR_USERNAME/RCS-sleep-pipeline.git

# Or if using SSH:
# git remote add origin git@github.com:YOUR_USERNAME/RCS-sleep-pipeline.git

# Push to GitHub
git branch -M main
git push -u origin main
```

## 3. Verify

Check that everything was pushed correctly:
- Visit: `https://github.com/YOUR_USERNAME/RCS-sleep-pipeline`
- Verify all files are present
- Check that README.md displays correctly

## Notes

- The `.gitignore` file is already configured to exclude:
  - Python cache files (`__pycache__/`)
  - Virtual environments (`venv/`, `RCS_env/`)
  - Data files (`.parquet`, `.csv`, `.xlsx`)
  - Temporary files (`temp_configs/`, `*.log`)
  - IDE files (`.vscode/`, `.idea/`)

- Config files have been sanitized (no hardcoded paths with personal information)

- If you need to update the repository later:
  ```bash
  git add .
  git commit -m "Your commit message"
  git push
  ```
